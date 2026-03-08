"""Cria e popula a planilha Google Sheets usada pelos workflows."""

import csv
import sys
from pathlib import Path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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

LOG_HEADERS = [
    "data_hora",
    "telefone",
    "nome",
    "segmento",
    "lead_id",
    "campanha_id",
    "imovel_id",
    "status",
    "provider_message_id",
    "provider_status",
    "mensagem",
]

ERROR_HEADERS = [
    "data_hora",
    "telefone",
    "nome",
    "segmento",
    "lead_id",
    "campanha_id",
    "imovel_id",
    "status",
    "erro_envio",
    "provider_status",
    "mensagem",
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


def get_credentials() -> Credentials:
    """Autentica via OAuth e persiste o token localmente."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            env_vars = read_env_file(PROJECT_DIR / ".env")

            client_id = env_vars.get("GOOGLE_DESKTOP_CLIENT_ID", "")
            client_secret = env_vars.get("GOOGLE_DESKTOP_CLIENT_SECRET", "")

            if not client_id or not client_secret:
                print("ERRO: GOOGLE_DESKTOP_CLIENT_ID e GOOGLE_DESKTOP_CLIENT_SECRET devem estar no .env")
                sys.exit(1)

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:0"],
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return creds


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
        lead["opt_in"] = row.get("opt_in", "sim")
        lead["renda_mensal"] = row.get("renda_mensal", "")
        lead["perfil"] = row.get("perfil", "")
        lead["segmento"] = segmento
        lead["nome_imovel"] = row.get("nome_imovel", "")
        lead["bairro"] = row.get("bairro", "")
        lead["faixa_preco"] = row.get("faixa_preco", "")
        lead["status_envio"] = ""
        lead["lead_id"] = row.get("lead_id", "")
        lead["campanha_id"] = row.get("campanha_id", "")
        lead["imovel_id"] = row.get("imovel_id", "")
        result.append(lead)
    return result


def main() -> None:
    print("=== Setup Google Sheets - Hogar Luxo ===\n")

    print("[1/5] Autenticando no Google...")
    creds = get_credentials()
    google_client = gspread.authorize(creds)
    print("  OK - Autenticado.\n")

    print("[2/5] Criando planilha 'Hogar Luxo - Leads WhatsApp'...")
    spreadsheet = google_client.create("Hogar Luxo - Leads WhatsApp")
    sheet_id = spreadsheet.id
    sheet_url = spreadsheet.url
    print(f"  OK - ID: {sheet_id}")
    print(f"  URL: {sheet_url}\n")

    print("[3/5] Criando abas...")
    ws_leads = spreadsheet.sheet1
    ws_leads.update_title("Leads")
    ws_leads.update([LEADS_HEADERS], "A1")

    ws_log = spreadsheet.add_worksheet(title="envios_log", rows=1000, cols=len(LOG_HEADERS))
    ws_log.update([LOG_HEADERS], "A1")

    ws_error = spreadsheet.add_worksheet(title="envios_erros", rows=1000, cols=len(ERROR_HEADERS))
    ws_error.update([ERROR_HEADERS], "A1")
    print("  OK - Abas: Leads, envios_log, envios_erros\n")

    print("[4/5] Importando leads dos CSVs...")

    clientes_file = SAIDA_DIR / "leads_import_clientes.csv"
    corretores_file = SAIDA_DIR / "leads_import_corretores_parceiros.csv"
    all_leads: list[dict[str, str]] = []

    if clientes_file.exists():
        clientes = map_csv_to_leads(read_csv(str(clientes_file)), "cliente")
        all_leads.extend(clientes)
        print(f"  Clientes: {len(clientes)} linhas")
    else:
        print(f"  AVISO: {clientes_file} nao encontrado")

    if corretores_file.exists():
        corretores = map_csv_to_leads(read_csv(str(corretores_file)), "corretor_parceiro")
        all_leads.extend(corretores)
        print(f"  Corretores/Parceiros: {len(corretores)} linhas")
    else:
        print(f"  AVISO: {corretores_file} nao encontrado")

    if all_leads:
        rows_data = [[lead[header] for header in LEADS_HEADERS] for lead in all_leads]
        batch_size = 1000
        total = len(rows_data)

        for index in range(0, total, batch_size):
            batch = rows_data[index : index + batch_size]
            start_row = index + 2
            cell_range = f"A{start_row}"
            ws_leads.update(batch, cell_range)
            batch_number = index // batch_size + 1
            end_row = min(index + batch_size, total)
            print(f"  Lote {batch_number}: linhas {index + 1}-{end_row} importadas")

        print(f"  Total: {total} leads importados\n")
    else:
        print("  Nenhum lead para importar.\n")

    print("[5/5] Atualizando .env com LEADS_SHEET_ID...")
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        upsert_env_value(env_file, "LEADS_SHEET_ID", sheet_id)
        print(f"  OK - LEADS_SHEET_ID={sheet_id}\n")
    else:
        print("  AVISO: .env nao encontrado. Adicione manualmente:")
        print(f"  LEADS_SHEET_ID={sheet_id}\n")

    print("=" * 50)
    print("SETUP COMPLETO!")
    print(f"  Sheet ID: {sheet_id}")
    print(f"  URL: {sheet_url}")
    print(f"  Leads: {len(all_leads)}")
    print()
    print("IMPORTANTE: todos os leads foram importados com opt_in='sim'.")
    print("Revise a coluna opt_in na planilha antes de disparar.")
    print()
    print("Proximo passo: reiniciar n8n para pegar o novo LEADS_SHEET_ID:")
    print("  docker compose up -d n8n")
    print("=" * 50)


if __name__ == "__main__":
    main()
