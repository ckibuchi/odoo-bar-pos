# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class DailyReconciliation(models.Model):
    _name = 'bar.reconciliation'
    _description = 'Daily Bar Reconciliation'
    _order = 'date desc'

    name = fields.Char('Reference', required=True, copy=False, readonly=True, default='New')
    date = fields.Date('Reconciliation Date', required=True, default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Stock count lines
    stock_line_ids = fields.One2many('bar.reconciliation.line', 'reconciliation_id', string='Stock Count')
    
    # Payments received
    mpesa_amount = fields.Monetary('MPESA Received', currency_field='currency_id', default=0.0)
    cash_amount = fields.Monetary('Cash from Cashier', currency_field='currency_id', default=0.0)
    expenses = fields.Monetary('Expenses Paid (Cash)', currency_field='currency_id', default=0.0,
                               help='Cash expenses that should be added back to expected cash')
    
    # Computed fields
    expected_sales = fields.Monetary('Expected Sales', compute='_compute_expected_sales', 
                                     store=True, currency_field='currency_id')
    total_received = fields.Monetary('Total Received', compute='_compute_totals', 
                                     store=True, currency_field='currency_id')
    variance = fields.Monetary('Variance (Shortage/Excess)', compute='_compute_variance', 
                               store=True, currency_field='currency_id')
    variance_percentage = fields.Float('Variance %', compute='_compute_variance', store=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    notes = fields.Text('Notes')
    user_id = fields.Many2one('res.users', string='Reconciled By', default=lambda self: self.env.user)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bar.reconciliation') or 'New'
        return super(DailyReconciliation, self).create(vals)
    
    @api.depends('stock_line_ids.sold_qty', 'stock_line_ids.sale_amount')
    def _compute_expected_sales(self):
        for rec in self:
            rec.expected_sales = sum(line.sale_amount for line in rec.stock_line_ids)
    
    @api.depends('mpesa_amount', 'cash_amount', 'expenses')
    def _compute_totals(self):
        for rec in self:
            rec.total_received = rec.mpesa_amount + rec.cash_amount + rec.expenses
    
    @api.depends('expected_sales', 'total_received')
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.total_received - rec.expected_sales
            if rec.expected_sales:
                rec.variance_percentage = (rec.variance / rec.expected_sales)
            else:
                rec.variance_percentage = 0.0
    
    def action_load_products(self):
        """Load all products with their current quantities"""
        self.ensure_one()
        
        # Clear existing lines
        self.stock_line_ids.unlink()
        
        # Get all products that should be tracked
        products = self.env['product.product'].search([
            ('sale_ok', '=', True),
            ('type', '=', 'product'),  # Only storable products
            ('active', '=', True)
        ])
        
        lines = []
        for product in products:
            lines.append((0, 0, {
                'product_id': product.id,
                'previous_qty': product.qty_available,
                'counted_qty': product.qty_available,  # Default to current, user will update
            }))
        
        self.stock_line_ids = lines
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Products Loaded',
                'message': f'{len(products)} products loaded. Update the counted quantities.',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_complete(self):
        """Complete the reconciliation and update stock"""
        self.ensure_one()
        
        if not self.stock_line_ids:
            raise UserError('Please add stock count lines before completing.')
        
        # Create inventory adjustment
        inventory = self.env['stock.quant'].with_context(inventory_mode=True)
        
        for line in self.stock_line_ids:
            if line.sold_qty != 0:
                # Find or create stock quant
                location = self.env.ref('stock.stock_location_stock')
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', location.id)
                ], limit=1)
                
                if quant:
                    quant.inventory_quantity = line.counted_qty
                    quant.action_apply_inventory()
        
        # Create accounting entries for cash/MPESA (simplified)
        # In production, you'd create proper journal entries here
        
        self.state = 'done'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reconciliation Complete',
                'message': f'Stock updated. Variance: {self.variance} {self.currency_id.symbol}',
                'type': 'success' if abs(self.variance) < 100 else 'warning',
                'sticky': False,
            }
        }
    
    def action_cancel(self):
        self.state = 'cancelled'
    
    def action_draft(self):
        self.state = 'draft'


class DailyReconciliationLine(models.Model):
    _name = 'bar.reconciliation.line'
    _description = 'Bar Reconciliation Line'

    reconciliation_id = fields.Many2one('bar.reconciliation', string='Reconciliation', 
                                        required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    
    # Stock quantities
    previous_qty = fields.Float('Previous Stock', digits='Product Unit of Measure')
    counted_qty = fields.Float('Counted Stock', digits='Product Unit of Measure', required=True)
    sold_qty = fields.Float('Sold Quantity', compute='_compute_sold_qty', store=True, 
                            digits='Product Unit of Measure')
    
    # Pricing
    unit_price = fields.Float('Unit Price', related='product_id.list_price', readonly=True)
    sale_amount = fields.Float('Sale Amount', compute='_compute_sale_amount', 
                            store=True, digits='Product Price')
    
    currency_id = fields.Many2one('res.currency', related='reconciliation_id.currency_id')
    
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', readonly=True)
    
    @api.depends('previous_qty', 'counted_qty')
    def _compute_sold_qty(self):
        for line in self:
            line.sold_qty = line.previous_qty - line.counted_qty
    
    @api.depends('sold_qty', 'unit_price')
    def _compute_sale_amount(self):
        for line in self:
            line.sale_amount = line.sold_qty * line.unit_price
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.previous_qty = self.product_id.qty_available
            self.counted_qty = self.product_id.qty_available