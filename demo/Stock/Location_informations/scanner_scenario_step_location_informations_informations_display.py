# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

report_stock_obj = pool.get('wms.report.stock.available')
report_stock_ids = report_stock_obj.search(cr, uid, [('location_id.name', '=', message)], context=context)

act = 'F'
res = [
    _('Location : %s') % message,
    '',
]

if not report_stock_ids:
    res.append(_('Empty location !'))

for report_stock in report_stock_obj.browse(cr, uid, report_stock_ids, context=context):
    res.extend([
        _('Product : [%s] %s') % (report_stock.product_id.default_code, report_stock.product_id.name),
        _('Quantity : %g %s') % (report_stock.product_qty, report_stock.uom_id.name),
        '',
    ])
