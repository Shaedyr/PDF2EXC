import requests

BRREG_BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter/"

def fetch_company_by_org(org_number: str) -> dict:
    """
    Fetches company data from BRREG's public API.
    Returns a dict with normalized fields or {} if not found.
    """

    if not org_number or not org_number.isdigit():
        return {}

    url = f"{BRREG_BASE_URL}{org_number}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return {}

    # Normalize fields so your merger + summary modules can use them
    out = {
        "orgnr": data.get("organisasjonsnummer"),
        "name": data.get("navn"),
        "address": extract_address(data),
        "poststed": extract_poststed(data),
        "postnummer": extract_postnummer(data),
        "company_summary": extract_summary_text(data),
    }

    return out


def extract_address(data: dict) -> str:
    addr = data.get("forretningsadresse") or {}
    return addr.get("adresse", [""])[0] if isinstance(addr.get("adresse"), list) else addr.get("adresse", "")


def extract_poststed(data: dict) -> str:
    addr = data.get("forretningsadresse") or {}
    return addr.get("poststed", "")


def extract_postnummer(data: dict) -> str:
    addr = data.get("forretningsadresse") or {}
    return addr.get("postnummer", "")


def extract_summary_text(data: dict) -> str:
    """
    Creates a human-readable summary for your Summary sheet.
    """
    navn = data.get("navn", "")
    orgnr = data.get("organisasjonsnummer", "")
    sektor = data.get("naeringskode1", {}).get("beskrivelse", "")
    etableringsdato = data.get("stiftelsesdato", "")

    parts = []

    if navn:
        parts.append(f"{navn}")
    if orgnr:
        parts.append(f"Org.nr: {orgnr}")
    if sektor:
        parts.append(f"Næringskode: {sektor}")
    if etableringsdato:
        parts.append(f"Etablert: {etableringsdato}")

    return " | ".join(parts)