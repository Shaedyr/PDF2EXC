from .cell_mapping import CELL_MAP
from app_modules.excel_filler import fill_excel

filled_bytes = fill_excel(
    template_bytes=template_bytes,
    field_values=merged_data,
    cell_map=CELL_MAP
)
