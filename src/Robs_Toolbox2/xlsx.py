import xlsxwriter
import xlsxwriter.worksheet
from dataclasses import dataclass, field


@dataclass
class SingleReport:
    filename: str
    output_format: dict
    results: dict
    dated: bool = True
    sheetname: str = 'Results'
    wb: xlsxwriter.Workbook = field(default=None, repr=False)
    ws: xlsxwriter.worksheet.Worksheet = None

    def __post_init__(self):
        self.wb = xlsxwriter.Workbook()
        self.ws = self.wb.add_worksheet(self.sheetname)

    def set_format(self):
        columns = []
        for enum, col in enumerate(self.output_format.keys()):
            head = {'header': col}
            update = self.output_format[col].get('header', {})
            head |= update
            columns.append(head)
            self.ws.set_column(enum, enum, self.output_format[col].get('col_width', 10))

    def set_values(self):
        for network in sorted(self.results.keys()):
            pass