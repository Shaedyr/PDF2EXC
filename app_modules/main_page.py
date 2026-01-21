import streamlit as st
from io import BytesIO
from openpyxl import load_workbook

from app_modules.template_loader import load_template
from app_modules.sheets.sammendrag.BRREG_info_getter import fetch_company_by_org
from app_modules.sheets.sammendrag.BRREG_Proff_info_getter_merger import merge_company_data
from app_modules.sheets.sammendrag.Summary_getter import generate_company_summary, place_summary
from app_modules.pdf_parser import extract_fields_from_pdf
from app_modules.excel_filler import fill_excel
from app_modules.Excel_download import download_excel_file
from app_modules.Sheets.Sammendrag.cell_mapping import CELL_MAP


def run():
    st.title("📄 PDF → Excel (Brønnøysund,Proff)")
    st.caption("Hent selskapsinformasjon og oppdater Excel automatisk")
    st.divider()

    # ---------------------------------------------------------
    # STEP 1: SEARCH BAR + RESULT DROPDOWN
    # ---------------------------------------------------------
    st.subheader("🔍 Finn selskap")

    query = st.text_input(
        "Søk etter selskap",
        placeholder="Skriv minst 2 bokstaver for å søke"
    )

    selected_company_raw = None
    company_options = []
    results = []

    # IMPORTANT: search_BRREG_live must exist in BRREG_info_getter
    from app_modules.Sheets.Sammendrag.BRREG_info_getter import search_BRREG_live

    if query and len(query) >= 2:
        results = search_BRREG_live(query) or []

        company_options = [
            f"{c.get('navn', '')} ({c.get('organisasjonsnummer', '')})"
            for c in results
        ]

    selected_label = st.selectbox(
        "Velg selskap",
        company_options,
        index=None,
        placeholder="Velg et selskap"
    )

    if selected_label:
        idx = company_options.index(selected_label)
        selected_company_raw = results[idx]

    pdf_bytes = st.file_uploader("Last opp PDF", type=["pdf"])

    if not selected_company_raw:
        st.info("Velg et selskap for å fortsette.")
        return

    # ---------------------------------------------------------
    # STEP 2: LOAD TEMPLATE
    # ---------------------------------------------------------
    if "template_bytes" not in st.session_state:
        st.session_state.template_bytes = load_template()

    template_bytes = st.session_state.template_bytes

    # ---------------------------------------------------------
    # STEP 3: FETCH COMPANY DATA (BRREG + Proff merger)
    # ---------------------------------------------------------
    org_number = selected_company_raw.get("organisasjonsnummer")
    company_data = merge_company_data(org_number)

    # ---------------------------------------------------------
    # STEP 4: SUMMARY
    # ---------------------------------------------------------
    summary_text = generate_company_summary(company_data)

    # ---------------------------------------------------------
    # STEP 5: PDF FIELDS
    # ---------------------------------------------------------
    pdf_fields = extract_fields_from_pdf(pdf_bytes) if pdf_bytes else {}

    # ---------------------------------------------------------
    # MERGE FIELDS
    # ---------------------------------------------------------
    merged_fields = {}
    merged_fields.update(company_data)
    merged_fields.update(pdf_fields)
    merged_fields["company_summary"] = summary_text

    st.divider()
    st.subheader("📋 Ekstraherte data")

    col_left, col_right = st.columns(2)

    with col_left:
        st.write("**Selskapsnavn:**", merged_fields.get("company_name", ""))
        st.write("**Organisasjonsnummer:**", merged_fields.get("org_number", ""))
        st.write("**Adresse:**", merged_fields.get("address", ""))
        st.write("**Postnummer:**", merged_fields.get("post_nr", ""))
        st.write("**Poststed:**", merged_fields.get("city", ""))
        st.write("**Antall ansatte:**", merged_fields.get("employees", ""))
        st.write("**Hjemmeside:**", merged_fields.get("homepage", ""))
        st.write("**NACE-kode:**", merged_fields.get("nace_code", ""))
        st.write("**NACE-beskrivelse:**", merged_fields.get("nace_description", ""))

    with col_right:
        st.markdown("**Sammendrag:**")
        st.info(summary_text or "Ingen tilgjengelig selskapsbeskrivelse.")

    st.divider()

    # ---------------------------------------------------------
    # STEP 6 + 7: PROCESS & DOWNLOAD
    # ---------------------------------------------------------
    if st.button("🚀 Prosesser & Oppdater Excel", use_container_width=True):
        with st.spinner("Behandler og fyller inn Excel..."):
            excel_bytes = fill_excel(
                template_bytes=template_bytes,
                field_values=merged_fields,
                cell_map=CELL_MAP
            )

            wb = load_workbook(filename=BytesIO(excel_bytes))
            ws = wb["Sammendrag"]
            place_summary(ws, summary_text)

            out = BytesIO()
            wb.save(out)
            out.seek(0)
            excel_bytes = out.getvalue()

        download_excel_file(
            excel_bytes=excel_bytes,
            company_name=merged_fields.get("company_name", "Selskap")
        )

