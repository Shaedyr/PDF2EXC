import requests
from bs4 import BeautifulSoup

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

    url =  f"https://www.proff.no/regnskap/{org_number}"

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
    out = {}
    try:
        table = soup.find("table", {"class": "table table-striped"})
        if not table:
            return out

        # Identify year columns
        header_cells = table.find("thead").find_all("th")
        years = {}
        for idx, th in enumerate(header_cells):
            text = th.get_text(strip=True)
            if text.isdigit():
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
                value = int(cleaned) if cleaned.isdigit() else None

                if "sum driftsinntekter" in label:
                    out[f"revenue_{year}"] = value
                elif "driftsresultat" in label:
                    out[f"driftsresultat_{year}"] = value
                elif ("resultat før skatt" in label or 
                      "ordinært resultat før skatt" in label):
                    out[f"resultat_for_skatt_{year}"] = value
                elif "sum eiend" in label:
                    out[f"sum_eiendeler_{year}"] = value
                elif "egenkapital" in label:
                    out[f"egenkapital_{year}"] = value

        return out
    except Exception:
        return out

# ---------------------------------------------------------
# Get_Proff_data
# ---------------------------------------------------------
def get_Proff_data(org_number: str) -> dict:
    print("get_Proff_data WAS CALLED")

def get_Proff_data(org_number: str) -> dict:
    html = fetch_Proff_html(org_number)

    if not html:
        print("No HTML returned from Proff.no")
        return {}

    print(html[:5000])   # TEMP DEBUG
    print("HTML LENGTH:", len(html))


    soup = BeautifulSoup(html, "html.parser")

    data = {}

    homepage = extract_homepage(soup)
    if homepage:
        data["homepage"] = homepage

    financials = extract_financials_all_years(soup)
    data.update(financials)

    return data

