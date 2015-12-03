# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

location = model.search([('name', '=', message)])

act = 'F'
res = [
    _('Found stock for location : %s') % location.name,
]

for location_info in env['stock.quant'].read_group(
    [('location_id.name', '=', message), ('location_id.usage', '=', 'internal')],
    ['location_id', 'lot_id', 'qty', 'product_id'],
    ['product_id'],
):
    product = env['product.product'].browse(location_info['product_id'][0])
    res.extend([
        '',
        _('Product : %s') % location_info['product_id'][1],
        _('Quantity : %g %s') % (location_info['qty'], product.uom_id.name),
    ])
