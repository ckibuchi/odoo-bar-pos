from odoo import models, fields, api, tools


class StockProjectedRevenue(models.Model):
    _name = 'stock.projected.revenue'
    _description = 'Stock Projected Revenue'
    _auto = False
    _order = 'product_name asc'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_name = fields.Char(string='Product Name', readonly=True)
    category_id = fields.Many2one('product.category', string='Category', readonly=True)
    qty_on_hand = fields.Float(string='Qty on Hand', digits=(16, 2), readonly=True)
    cost_price = fields.Float(string='Cost Price', digits=(16, 2), readonly=True)
    sale_price = fields.Float(string='Sale Price', digits=(16, 2), readonly=True)
    total_cost_value = fields.Float(string='Total Cost Value', digits=(16, 2), readonly=True)
    projected_revenue = fields.Float(string='Projected Revenue', digits=(16, 2), readonly=True)
    potential_profit = fields.Float(string='Potential Profit', digits=(16, 2), readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW stock_projected_revenue AS (
                SELECT
                    pp.id                                           AS id,
                    pp.id                                           AS product_id,
                    pt.name                                         AS product_name,
                    pt.categ_id                                     AS category_id,
                    COALESCE(sq.qty, 0)                             AS qty_on_hand,
                    pt.standard_price                               AS cost_price,
                    pt.list_price                                   AS sale_price,
                    COALESCE(sq.qty, 0) * pt.standard_price         AS total_cost_value,
                    COALESCE(sq.qty, 0) * pt.list_price             AS projected_revenue,
                    (COALESCE(sq.qty, 0) * pt.list_price)
                        - (COALESCE(sq.qty, 0) * pt.standard_price) AS potential_profit,
                    rc.id                                           AS currency_id
                FROM product_product pp
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN (
                    SELECT
                        product_id,
                        SUM(quantity) AS qty
                    FROM stock_quant sq2
                    JOIN stock_location sl ON sl.id = sq2.location_id
                    WHERE sl.usage = 'internal'
                    GROUP BY product_id
                ) sq ON sq.product_id = pp.id
                JOIN res_company rc_comp ON rc_comp.id = (
                    SELECT id FROM res_company ORDER BY id LIMIT 1
                )
                JOIN res_currency rc ON rc.id = rc_comp.currency_id
                WHERE pt.type = 'product'
                AND pt.active = TRUE
                AND pp.active = TRUE
                AND COALESCE(sq.qty, 0) > 0
            )
        """)

    def action_print_pdf(self):
        return self.env.ref(
            'stock_projected_revenue.action_report_stock_projected_revenue'
        ).report_action(self)

    def action_export_xlsx(self):
        return self.env.ref(
            'stock_projected_revenue.action_report_stock_projected_revenue_xlsx'
        ).report_action(self)
