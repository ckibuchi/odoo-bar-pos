# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_bar_product = fields.Boolean('Bar Product', default=True, 
                                    help='Include this product in daily reconciliation')