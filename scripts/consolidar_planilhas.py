#!/usr/bin/env python3
"""
Consolida exportacoes de grupos de WhatsApp (Dealssup) em CSVs limpos.

Entrada esperada:
- arquivos .xlsx/.csv na pasta ./planilhas

Saida:
- ./saida/contatos_raw.csv
- ./saida/contatos_unificados.csv
- ./saida/clientes.csv
- ./saida/corretores_parceiros.csv
- ./saida/indefinidos.csv
- ./saida/duplicados_telefone.csv
- ./saida/planilha_mestre_clean.csv
- ./saida/planilha_mestre_sem_duplicados.csv
- ./saida/classificacao_grupos.csv
- ./saida/resumo_consolidacao.txt
"""

from __future__ import annotations

import csv
import re
import unicodedata
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "planilhas"
OUTPUT_DIR = ROOT / "saida"


NS_MAIN = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
NS_REL_WORKBOOK = {"r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
NS_REL_PACKAGE = {"x": "http://schemas.openxmlformats.org/package/2006/relationships"}


BROKER_KEYWORDS = {
    "corretor",
    "corretores",
    "parceiro",
    "parceiros",
    "imobili",
    "imovel",
    "imoveis",
    "negocios",
    "revenda",
    "terreno",
    "terrenos",
    "areas",
    "fazenda",
    "fazendas",
    "construtor",
    "construtores",
    "ebm",
    "hogar",
    "milfazendas",
}


CSV_FIELDS = [
    "source_file",
    "source_group",
    "segmento",
    "segmento_motivo",
    "country_code",
    "country_name",
    "phone_number",
    "formatted_phone",
    "phone_digits",
    "whatsapp_e164",
    "is_my_contact",
    "saved_name",
    "public_name",
    "display_name",
    "is_business",
    "is_admin",
    "labels",
]


@dataclass
class Row:
    source_file: str
    source_group: str
    segmento: str
    segmento_motivo: str
    country_code: str
    country_name: str
    phone_number: str
    formatted_phone: str
    phone_digits: str
    whatsapp_e164: str
    is_my_contact: str
    saved_name: str
    public_name: str
    display_name: str
    is_business: str
    is_admin: str
    labels: str

    def as_dict(self) -> Dict[str, str]:
        return {field: str(getattr(self, field, "")) for field in CSV_FIELDS}


def normalize_text(value: str) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return value.lower()


def classify_group(group_name: str) -> Tuple[str, str]:
    norm = normalize_text(group_name)
    for keyword in BROKER_KEYWORDS:
        if keyword in norm:
            return "corretor_parceiro", f"nome_do_grupo_contem:{keyword}"
    return "cliente", "default_cliente"


def group_name_from_filename(file_name: str) -> str:
    name = file_name
    name = re.sub(r"\s+(Excel|CSV)\s+Results(?:\s*\(\d+\))?$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\.xlsx$|\.csv$", "", name, flags=re.IGNORECASE)
    return name.strip()


def to_digits(value: str) -> str:
    return re.sub(r"\D+", "", value or "")


def format_e164(digits: str, country_code: str) -> str:
    if not digits:
        return ""
    cc = to_digits(country_code)
    if cc and not digits.startswith(cc):
        return f"+{cc}{digits}"
    return f"+{digits}"


def canonical_phone(digits: str, country_code: str) -> str:
    d = to_digits(digits)
    cc = to_digits(country_code)
    if not d:
        return ""
    # Regra BR: se vier sem DDI mas com 10/11 digitos, prefixa 55
    if cc == "55":
        if d.startswith("55"):
            return d
        if len(d) in (10, 11):
            return "55" + d
    if cc and not d.startswith(cc):
        return cc + d
    return d


def col_to_index(col_ref: str) -> int:
    idx = 0
    for ch in col_ref:
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def read_xlsx_rows(path: Path) -> List[List[str]]:
    with zipfile.ZipFile(path) as zf:
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root_ss = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root_ss.findall("m:si", NS_MAIN):
                shared_strings.append("".join(t.text or "" for t in si.findall(".//m:t", NS_MAIN)))

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        first_sheet = workbook.find("m:sheets/m:sheet", {**NS_MAIN, **NS_REL_WORKBOOK})
        if first_sheet is None:
            return []
        rid = first_sheet.attrib.get(f"{{{NS_REL_WORKBOOK['r']}}}id")
        if not rid:
            return []

        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        target = None
        for rel in rels.findall("x:Relationship", NS_REL_PACKAGE):
            if rel.attrib.get("Id") == rid:
                target = rel.attrib.get("Target")
                break
        if not target:
            return []

        if target.startswith("/"):
            sheet_path = target.lstrip("/")
        else:
            sheet_path = f"xl/{target.lstrip('/')}"
        sheet_path = sheet_path.replace("\\", "/")
        sheet_xml = ET.fromstring(zf.read(sheet_path))

        rows: List[List[str]] = []
        for row in sheet_xml.findall("m:sheetData/m:row", NS_MAIN):
            cells: Dict[int, str] = {}
            for cell in row.findall("m:c", NS_MAIN):
                cell_ref = cell.attrib.get("r", "")
                match = re.match(r"([A-Z]+)", cell_ref)
                if not match:
                    continue
                idx = col_to_index(match.group(1))
                cell_type = cell.attrib.get("t")
                value = ""

                if cell_type == "inlineStr":
                    is_node = cell.find("m:is", NS_MAIN)
                    if is_node is not None:
                        value = "".join(t.text or "" for t in is_node.findall(".//m:t", NS_MAIN))
                else:
                    v_node = cell.find("m:v", NS_MAIN)
                    raw = v_node.text if v_node is not None and v_node.text is not None else ""
                    if cell_type == "s" and raw.isdigit():
                        pos = int(raw)
                        value = shared_strings[pos] if 0 <= pos < len(shared_strings) else ""
                    else:
                        value = raw

                cells[idx] = value

            if not cells:
                continue
            max_idx = max(cells.keys())
            out = [""] * (max_idx + 1)
            for i, val in cells.items():
                out[i] = val
            rows.append(out)
        return rows


def read_csv_rows(path: Path) -> List[List[str]]:
    rows: List[List[str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows


def rows_to_dicts(rows: List[List[str]]) -> List[Dict[str, str]]:
    if not rows:
        return []
    headers = [h.strip() for h in rows[0]]
    out: List[Dict[str, str]] = []
    for row in rows[1:]:
        values = row + [""] * (len(headers) - len(row))
        obj = {headers[i]: values[i] for i in range(len(headers))}
        if any((v or "").strip() for v in obj.values()):
            out.append(obj)
    return out


def read_records(file_path: Path) -> List[Dict[str, str]]:
    suffix = file_path.suffix.lower()
    if suffix == ".xlsx":
        return rows_to_dicts(read_xlsx_rows(file_path))
    if suffix == ".csv":
        return rows_to_dicts(read_csv_rows(file_path))
    return []


def write_csv(path: Path, rows: Iterable[Dict[str, str]], fieldnames: List[str]) -> int:
    count = 0
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in INPUT_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".xlsx", ".csv"}])
    if not files:
        raise SystemExit(f"Nenhum arquivo .xlsx/.csv encontrado em {INPUT_DIR}")

    raw_rows: List[Row] = []
    errors: List[str] = []

    for file_path in files:
        group_name = group_name_from_filename(file_path.name)
        segment, reason = classify_group(group_name)
        try:
            records = read_records(file_path)
        except Exception as exc:
            errors.append(f"{file_path.name}: {exc}")
            continue

        for rec in records:
            phone_number = (rec.get("phone_number") or "").strip()
            country_code = (rec.get("country_code") or "").strip()
            phone_digits_raw = to_digits(phone_number) or to_digits(rec.get("formatted_phone", ""))
            phone_digits = canonical_phone(phone_digits_raw, country_code)
            if not phone_digits:
                continue
            row = Row(
                source_file=file_path.name,
                source_group=group_name,
                segmento=segment,
                segmento_motivo=reason,
                country_code=country_code,
                country_name=(rec.get("country_name") or "").strip(),
                phone_number=phone_number,
                formatted_phone=(rec.get("formatted_phone") or "").strip(),
                phone_digits=phone_digits,
                whatsapp_e164=format_e164(phone_digits, country_code),
                is_my_contact=(rec.get("is_my_contact") or "").strip(),
                saved_name=(rec.get("saved_name") or "").strip(),
                public_name=(rec.get("public_name") or "").strip(),
                display_name=((rec.get("saved_name") or "").strip() or (rec.get("public_name") or "").strip()),
                is_business=(rec.get("is_business") or "").strip(),
                is_admin=(rec.get("is_admin") or "").strip(),
                labels=(rec.get("labels") or "").strip(),
            )
            raw_rows.append(row)

    # raw
    raw_dicts = [r.as_dict() for r in raw_rows]
    write_csv(OUTPUT_DIR / "contatos_raw.csv", raw_dicts, CSV_FIELDS)

    # agrupamento por telefone
    grouped: Dict[str, List[Row]] = defaultdict(list)
    for r in raw_rows:
        grouped[r.phone_digits].append(r)

    unified_fields = [
        "phone_digits",
        "whatsapp_e164",
        "display_name",
        "saved_name",
        "public_name",
        "country_code",
        "country_name",
        "segmento",
        "sources_count",
        "source_groups",
        "source_files",
        "is_business",
        "is_admin",
        "is_my_contact",
        "labels",
    ]

    unified_rows: List[Dict[str, str]] = []
    dup_rows: List[Dict[str, str]] = []

    for phone, items in grouped.items():
        items_sorted = sorted(items, key=lambda x: (x.segmento != "corretor_parceiro", x.source_group))
        base = items_sorted[0]
        groups = sorted({i.source_group for i in items})
        files_used = sorted({i.source_file for i in items})
        has_broker = any(i.segmento == "corretor_parceiro" for i in items)
        final_segment = "corretor_parceiro" if has_broker else "cliente"

        unified_rows.append(
            {
                "phone_digits": phone,
                "whatsapp_e164": base.whatsapp_e164,
                "display_name": base.display_name,
                "saved_name": base.saved_name,
                "public_name": base.public_name,
                "country_code": base.country_code,
                "country_name": base.country_name,
                "segmento": final_segment,
                "sources_count": str(len(items)),
                "source_groups": " | ".join(groups),
                "source_files": " | ".join(files_used),
                "is_business": base.is_business,
                "is_admin": base.is_admin,
                "is_my_contact": base.is_my_contact,
                "labels": base.labels,
            }
        )

        if len(items) > 1:
            for i in items:
                dup_rows.append(
                    {
                        "phone_digits": i.phone_digits,
                        "whatsapp_e164": i.whatsapp_e164,
                        "display_name": i.display_name,
                        "saved_name": i.saved_name,
                        "public_name": i.public_name,
                        "country_code": i.country_code,
                        "country_name": i.country_name,
                        "segmento": i.segmento,
                        "source_file": i.source_file,
                        "source_group": i.source_group,
                        "is_business": i.is_business,
                        "is_admin": i.is_admin,
                        "is_my_contact": i.is_my_contact,
                        "labels": i.labels,
                    }
                )

    unified_rows.sort(key=lambda x: (x["segmento"], x["display_name"], x["phone_digits"]))
    write_csv(OUTPUT_DIR / "contatos_unificados.csv", unified_rows, unified_fields)

    clients = [r for r in unified_rows if r["segmento"] == "cliente"]
    brokers = [r for r in unified_rows if r["segmento"] == "corretor_parceiro"]
    unknown = [r for r in unified_rows if r["segmento"] not in {"cliente", "corretor_parceiro"}]

    write_csv(OUTPUT_DIR / "clientes.csv", clients, unified_fields)
    write_csv(OUTPUT_DIR / "corretores_parceiros.csv", brokers, unified_fields)
    write_csv(OUTPUT_DIR / "indefinidos.csv", unknown, unified_fields)

    dup_fields = [
        "phone_digits",
        "whatsapp_e164",
        "display_name",
        "saved_name",
        "public_name",
        "country_code",
        "country_name",
        "segmento",
        "source_file",
        "source_group",
        "is_business",
        "is_admin",
        "is_my_contact",
        "labels",
    ]
    write_csv(OUTPUT_DIR / "duplicados_telefone.csv", dup_rows, dup_fields)

    clean_fields = [
        "telefone",
        "whatsapp",
        "nome",
        "categoria",
        "qtd_grupos",
        "grupos_origem",
        "arquivos_origem",
        "eh_contato_salvo",
        "eh_negocio",
        "eh_admin",
    ]
    clean_rows = [
        {
            "telefone": r["phone_digits"],
            "whatsapp": r["whatsapp_e164"],
            "nome": r["display_name"],
            "categoria": "Corretor/Parceiro" if r["segmento"] == "corretor_parceiro" else "Cliente",
            "qtd_grupos": r["sources_count"],
            "grupos_origem": r["source_groups"],
            "arquivos_origem": r["source_files"],
            "eh_contato_salvo": r["is_my_contact"],
            "eh_negocio": r["is_business"],
            "eh_admin": r["is_admin"],
        }
        for r in unified_rows
    ]
    write_csv(OUTPUT_DIR / "planilha_mestre_clean.csv", clean_rows, clean_fields)
    write_csv(OUTPUT_DIR / "planilha_mestre_sem_duplicados.csv", clean_rows, clean_fields)

    group_rows = []
    by_group: Dict[str, List[Row]] = defaultdict(list)
    for row in raw_rows:
        by_group[row.source_group].append(row)
    for group_name, items in sorted(by_group.items(), key=lambda kv: kv[0].lower()):
        phones = {i.phone_digits for i in items}
        group_rows.append(
            {
                "grupo": group_name,
                "categoria": "Corretor/Parceiro" if items[0].segmento == "corretor_parceiro" else "Cliente",
                "motivo": items[0].segmento_motivo,
                "contatos_raw": str(len(items)),
                "telefones_unicos": str(len(phones)),
            }
        )
    group_fields = ["grupo", "categoria", "motivo", "contatos_raw", "telefones_unicos"]
    write_csv(OUTPUT_DIR / "classificacao_grupos.csv", group_rows, group_fields)

    total_raw = len(raw_rows)
    total_unique = len(unified_rows)
    total_dup_numbers = sum(1 for rows in grouped.values() if len(rows) > 1)
    total_clientes = len(clients)
    total_corretores = len(brokers)

    mestre_phones = [r["telefone"] for r in clean_rows]
    mestre_dup_restante = len(mestre_phones) - len(set(mestre_phones))

    summary = [
        "Resumo consolidacao Dealssup",
        f"Arquivos lidos: {len(files)}",
        f"Linhas validas (raw): {total_raw}",
        f"Telefones unicos: {total_unique}",
        f"Telefones duplicados: {total_dup_numbers}",
        f"Clientes unicos: {total_clientes}",
        f"Corretores/Parceiros unicos: {total_corretores}",
        f"Indefinidos unicos: {len(unknown)}",
        f"Duplicados restantes na planilha mestre: {mestre_dup_restante}",
        "",
        "Arquivos de saida:",
        "- contatos_raw.csv",
        "- contatos_unificados.csv",
        "- clientes.csv",
        "- corretores_parceiros.csv",
        "- indefinidos.csv",
        "- duplicados_telefone.csv",
        "- planilha_mestre_clean.csv",
        "- planilha_mestre_sem_duplicados.csv",
        "- classificacao_grupos.csv",
    ]
    if errors:
        summary += ["", "Erros de leitura:"] + [f"- {err}" for err in errors]

    (OUTPUT_DIR / "resumo_consolidacao.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
