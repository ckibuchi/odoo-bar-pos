{
    'name': 'Stock Projected Revenue',
    'version': '16.0.1.0.0',
    'summary': 'Report showing projected revenue from current stock (Qty x Sale Price)',
    'description': """
        Adds a report under Inventory > Reporting that shows:
        - Product Name
        - Quantity on Hand
        - Cost Price
        - Total Cost Value (Cost x Qty)
        - Sale Price
        - Projected Revenue (Sale Price x Qty)
        - Potential Profit (Projected Revenue - Total Cost)
        - Report generated date and time
    """,
    'category': 'Inventory',
    'author': 'Custom',
    'depends': ['stock', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_projected_revenue_view.xml',
        'report/stock_projected_revenue_report.xml',
        'report/stock_projected_revenue_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
