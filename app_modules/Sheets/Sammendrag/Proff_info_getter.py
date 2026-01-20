import requests
from bs4 import BeautifulSoup

PROFF_BASE_URL = "https://www.proff.no/selskap/{orgnr}"

# ---------------------------------------------------------
# Fetch HTML from Proff.no
# ---------------------------------------------------------
def fetch_Proff_html(org_number: str):
    """
    Downloads the Proff.no company page for the given org number.
    Returns HTML text or None.
    """
    if not org_number or not org_number.isdigit():
        return None

    url = PROFF_BASE_URL.format(orgnr=org_number)

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception:
        return None

# ---------------------------------------------------------
# Extract homepage
# ---------------------------------------------------------
def extract_homepage(soup: BeautifulSoup) -> str:
    """
    Extracts homepage URL from Proff company profile.
    """
    try:
        # Look for link with "Hjemmeside"
        link = soup.find("a", href=True, string=lambda t: t and "hjemmeside" in t.lower())
        if link:
            return link["href"].strip()

        # Fallback: look for any external link in company info box
        info_box = soup.find("div", {"class": "company-info"})
        if info_box:
            a = info_box.find("a", href=True)
            if a and "proff.no" not in a["href"]:
                return a["href"].strip()
    except Exception:
        pass
    return ""

# ---------------------------------------------------------
# Extract financials for all available years
# ---------------------------------------------------------
def extract_financials_all_years(soup: BeautifulSoup) -> dict:
    """
    Extracts revenue, EBIT (driftsresultat), and result before tax
    for all available years (e.g. 2022, 2023, 2024).
    Returns a dict keyed by year.
    """
    out = {}
    try:
        table = soup.find("table", {"class": "financial-table"})
        if not table:
            return out

        # Identify year columns from header
        header_cells = table.find("thead").find_all("th")
        years = {}
        for idx, th in enumerate(header_cells):
            text = th.get_text(strip=True)
            if text.isdigit():  # e.g. "2022", "2023", "2024"
                years[text] = idx

        rows = table.find("tbody").find_all("tr")

        for year, idx in years.items():
            for row in rows:
                label = row.find("td").get_text(strip=True).lower()
                cells = row.find_all("td")
                if idx >= len(cells):
                    continue

                raw_value = cells[idx].get_text(strip=True)
                cleaned = raw_value.replace(" ", "").replace(".", "").replace(",", "")
                value = int(cleaned) * 1000 if cleaned.isdigit() else None

                if "sum driftsinntekter" in label:
                    out[f"revenue_{year}"] = value
                elif "driftsresultat" in label:
                    out[f"driftsresultat_{year}"] = value
                elif "resultat før skatt" in label or "ord. res. f. skatt" in label:
                    out[f"resultat_for_skatt_{year}"] = value
                elif "sum eiend" in label:
                    out[f"sum_eiendeler_{year}"] = value
                elif "egenkapital" in label:
                    out[f"egenkapital_{year}"] = value
        return out
    except Exception:
        return out

# ---------------------------------------------------------
# High-level wrapper
# ---------------------------------------------------------
def get_Proff_data(org_number: str) -> dict:
    """
    High-level wrapper: fetches Proff HTML and extracts homepage + multi-year financials.
    Returns a dict with keys used by the merger and Excel filler.
    """
    html = fetch_Proff_html(org_number)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    data = {}

    # Homepage
    homepage = extract_homepage(soup)
    if homepage:
        data["homepage"] = homepage

    # Multi-year financials (2022, 2023, 2024)
    financials = extract_financials_all_years(soup)
    data.update(financials)

    return data
