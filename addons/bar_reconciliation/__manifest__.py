# -*- coding: utf-8 -*-
{
    'name': 'Bar Daily Reconciliation',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Daily stock count and cash reconciliation for bars',
    'description': """
        Simplified daily reconciliation workflow:
        - Count physical stock
        - System calculates sales automatically
        - Enter MPESA and cash received
        - Automatic variance calculation
    """,
    'author': 'Your Name',
    'depends': ['base', 'stock', 'point_of_sale', 'account'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/daily_reconciliation_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}