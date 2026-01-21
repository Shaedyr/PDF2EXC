import requests
from bs4 import BeautifulSoup


def fetch_Proff_html(org_number: str):
    if not org_number or not org_number.isdigit():
        return None

    url = f"https://www.proff.no/regnskap/{org_number}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def extract_financials_all_years(soup: BeautifulSoup) -> dict:
    out = {}

    table = soup.find("table")
    if not table:
        return out

    rows = table.find_all("tr")
    if not rows:
        return out

    header_cells = rows[0].find_all(["th", "td"])
    years = {}
    for idx, cell in enumerate(header_cells):
        text = cell.get_text(strip=True)
        if text.isdigit():
            years[text] = idx

    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue

        label = cells[0].get_text(strip=True).lower()

        for year, idx in years.items():
            if idx >= len(cells):
                continue

            raw = cells[idx].get_text(strip=True)
            cleaned = raw.replace(" ", "").replace(".", "").replace(",", "")
            value = int(cleaned) if cleaned.isdigit() else None

            if "driftsinntekter" in label:
                out[f"revenue_{year}"] = value
            elif "driftsresultat" in label:
                out[f"driftsresultat_{year}"] = value
            elif "resultat før skatt" in label:
                out[f"resultat_for_skatt_{year}"] = value

    return out


def get_Proff_data(org_number: str) -> dict:
    html = fetch_Proff_html(org_number)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    data = extract_financials_all_years(soup)
    return data
