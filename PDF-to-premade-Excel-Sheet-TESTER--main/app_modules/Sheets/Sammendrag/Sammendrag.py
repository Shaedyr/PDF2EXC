from .cell_mapping import CELL_MAP
from app_modules.excel_filler import fill_excel

filled_bytes = fill_excel(template_bytes, merged_data, CELL_MAP)

