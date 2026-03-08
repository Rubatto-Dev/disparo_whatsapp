"""Reimporta os leads em uma planilha Google Sheets ja existente."""

import csv
import sys
from pathlib import Path

import gspread
from google.oauth2.credentials import Credentials

PROJECT_DIR = Path(__file__).resolve().parent.parent
SAIDA_DIR = PROJECT_DIR / "saida"
TOKEN_FILE = PROJECT_DIR / "google_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

LEADS_HEADERS = [
    "nome",
    "telefone",
    "opt_in",
    "renda_mensal",
    "perfil",
    "segmento",
    "nome_imovel",
    "bairro",
    "faixa_preco",
    "status_envio",
    "lead_id",
    "campanha_id",
    "imovel_id",
    "ultimo_envio_em",
    "provider_message_id",
    "provider_status",
    "erro_envio",
]


def read_env_file(path: Path) -> dict[str, str]:
    env_vars: dict[str, str] = {}
    if not path.exists():
        return env_vars

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        env_vars[key.strip()] = value.strip()

    return env_vars


def upsert_env_value(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    new_line = f"{key}={value}"
    updated = False
    output: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}="):
            output.append(new_line)
            updated = True
        else:
            output.append(line)

    if not updated:
        if output and output[-1] != "":
            output.append("")
        output.append(new_line)

    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def resolve_sheet_id() -> str:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()

    env_vars = read_env_file(PROJECT_DIR / ".env")
    sheet_id = env_vars.get("LEADS_SHEET_ID", "").strip()
    if sheet_id:
        return sheet_id

    raise SystemExit(
        "ERRO: informe o SHEET_ID como argumento ou configure LEADS_SHEET_ID no arquivo .env."
    )


def read_csv(filepath: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            with open(filepath, "r", encoding=encoding, newline="") as file_handle:
                reader = csv.DictReader(file_handle)
                rows.extend(reader)
            return rows
        except (UnicodeDecodeError, UnicodeError):
            rows = []
    return rows


def map_csv_to_leads(csv_rows: list[dict[str, str]], segmento: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in csv_rows:
        lead = {header: "" for header in LEADS_HEADERS}
        lead["nome"] = row.get("nome", "")
        lead["telefone"] = row.get("telefone", "")
        lead["opt_in"] = "sim"
        lead["renda_mensal"] = row.get("renda_mensal", "")
        lead["perfil"] = row.get("perfil", "")
        lead["segmento"] = segmento
        lead["nome_imovel"] = row.get("nome_imovel", "")
        lead["bairro"] = row.get("bairro", "")
        lead["faixa_preco"] = row.get("faixa_preco", "")
        lead["lead_id"] = row.get("lead_id", "")
        lead["campanha_id"] = row.get("campanha_id", "")
        lead["imovel_id"] = row.get("imovel_id", "")
        result.append(lead)
    return result


def main() -> None:
    sheet_id = resolve_sheet_id()

    print("Conectando ao Google Sheets...")
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    google_client = gspread.authorize(creds)
    spreadsheet = google_client.open_by_key(sheet_id)
    ws_leads = spreadsheet.worksheet("Leads")

    print("Lendo CSVs...")
    all_leads: list[dict[str, str]] = []

    clientes = map_csv_to_leads(read_csv(str(SAIDA_DIR / "leads_import_clientes.csv")), "cliente")
    all_leads.extend(clientes)
    print(f"  Clientes: {len(clientes)}")

    corretores = map_csv_to_leads(
        read_csv(str(SAIDA_DIR / "leads_import_corretores_parceiros.csv")),
        "corretor_parceiro",
    )
    all_leads.extend(corretores)
    print(f"  Corretores: {len(corretores)}")

    total = len(all_leads)
    print(f"  Total: {total}")

    needed_rows = total + 10
    print(f"Expandindo aba Leads para {needed_rows} linhas...")
    ws_leads.resize(rows=needed_rows, cols=len(LEADS_HEADERS))

    print("Limpando dados antigos...")
    ws_leads.batch_clear(["A2:Q10000"])

    rows_data = [[lead[header] for header in LEADS_HEADERS] for lead in all_leads]
    batch_size = 1000
    for index in range(0, total, batch_size):
        batch = rows_data[index : index + batch_size]
        start_row = index + 2
        cell_range = f"A{start_row}"
        ws_leads.update(batch, cell_range)
        end_row = min(index + batch_size, total)
        print(f"  Lote {index // batch_size + 1}: linhas {index + 1}-{end_row} importadas")

    print(f"\nImportacao completa! {total} leads na planilha.")
    print(f"URL: https://docs.google.com/spreadsheets/d/{sheet_id}")

    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        upsert_env_value(env_file, "LEADS_SHEET_ID", sheet_id)
        print(f"  .env atualizado: LEADS_SHEET_ID={sheet_id}")


if __name__ == "__main__":
    main()
