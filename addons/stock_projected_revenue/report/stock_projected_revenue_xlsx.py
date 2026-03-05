from odoo import models
from datetime import datetime


class StockProjectedRevenueXlsx(models.AbstractModel):
    _name = 'report.stock_projected_revenue.report_stock_projected_revenue_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Stock Projected Revenue XLSX Report'

    def generate_xlsx_report(self, workbook, data, records):
        # Formats
        title_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center',
            'valign': 'vcenter', 'font_color': '#FFFFFF',
            'bg_color': '#875A7B', 'border': 1
        })
        header_format = workbook.add_format({
            'bold': True, 'font_size': 10, 'align': 'center',
            'valign': 'vcenter', 'font_color': '#FFFFFF',
            'bg_color': '#875A7B', 'border': 1, 'text_wrap': True
        })
        date_format = workbook.add_format({
            'italic': True, 'font_size': 9,
            'align': 'center', 'font_color': '#666666'
        })
        row_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'valign': 'vcenter'
        })
        row_alt_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'valign': 'vcenter',
            'bg_color': '#F9F0FF'
        })
        number_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'num_format': '#,##0.00',
            'align': 'right'
        })
        number_alt_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'num_format': '#,##0.00',
            'align': 'right', 'bg_color': '#F9F0FF'
        })
        total_format = workbook.add_format({
            'bold': True, 'font_size': 10, 'border': 1,
            'num_format': '#,##0.00', 'align': 'right',
            'bg_color': '#E8D5F5'
        })
        total_label_format = workbook.add_format({
            'bold': True, 'font_size': 10, 'border': 1,
            'align': 'right', 'bg_color': '#E8D5F5'
        })

        # Sheet
        sheet = workbook.add_worksheet('Projected Revenue')
        sheet.set_zoom(85)

        # Column widths
        sheet.set_column('A:A', 6)   # #
        sheet.set_column('B:B', 35)  # Product
        sheet.set_column('C:C', 20)  # Category
        sheet.set_column('D:D', 14)  # Qty
        sheet.set_column('E:E', 14)  # Cost Price
        sheet.set_column('F:F', 14)  # Sale Price
        sheet.set_column('G:G', 18)  # Total Cost
        sheet.set_column('H:H', 20)  # Projected Revenue
        sheet.set_column('I:I', 18)  # Potential Profit

        # Title row
        sheet.merge_range('A1:I1', 'STOCK PROJECTED REVENUE REPORT', title_format)
        sheet.set_row(0, 30)

        # Date row
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        sheet.merge_range('A2:I2', f'Generated on: {now}', date_format)
        sheet.set_row(1, 18)

        # Summary totals row
        total_cost = sum(records.mapped('total_cost_value'))
        total_revenue = sum(records.mapped('projected_revenue'))
        total_profit = sum(records.mapped('potential_profit'))

        summary_label = workbook.add_format({
            'bold': True, 'font_size': 10, 'border': 1,
            'align': 'center', 'bg_color': '#D5E8D4'
        })
        summary_value = workbook.add_format({
            'bold': True, 'font_size': 10, 'border': 1,
            'num_format': '#,##0.00', 'align': 'center',
            'bg_color': '#D5E8D4'
        })

        sheet.merge_range('A3:C3', 'Total Stock Cost Value', summary_label)
        sheet.merge_range('D3:F3', f'{total_cost:,.2f}', summary_value)
        sheet.merge_range('G3:G3', 'Total Projected Revenue', summary_label)
        sheet.merge_range('H3:I3', f'{total_revenue:,.2f}', summary_value)
        sheet.set_row(2, 22)

        # Blank row
        sheet.set_row(3, 8)

        # Header row
        headers = [
            '#', 'Product Name', 'Category', 'Qty on Hand',
            'Cost Price', 'Sale Price', 'Total Cost Value',
            'Projected Revenue', 'Potential Profit'
        ]
        for col, header in enumerate(headers):
            sheet.write(4, col, header, header_format)
        sheet.set_row(4, 30)

        # Data rows
        row = 5
        for idx, line in enumerate(records, start=1):
            fmt = row_format if idx % 2 != 0 else row_alt_format
            nfmt = number_format if idx % 2 != 0 else number_alt_format
            sheet.write(row, 0, idx, fmt)
            sheet.write(row, 1, line.product_name or '', fmt)
            sheet.write(row, 2, line.category_id.name or '', fmt)
            sheet.write(row, 3, line.qty_on_hand, nfmt)
            sheet.write(row, 4, line.cost_price, nfmt)
            sheet.write(row, 5, line.sale_price, nfmt)
            sheet.write(row, 6, line.total_cost_value, nfmt)
            sheet.write(row, 7, line.projected_revenue, nfmt)
            sheet.write(row, 8, line.potential_profit, nfmt)
            row += 1

        # Totals row
        sheet.merge_range(row, 0, row, 5, 'TOTALS', total_label_format)
        sheet.write(row, 6, total_cost, total_format)
        sheet.write(row, 7, total_revenue, total_format)
        sheet.write(row, 8, total_profit, total_format)
        sheet.set_row(row, 22)

        # Freeze header
        sheet.freeze_panes(5, 0)
