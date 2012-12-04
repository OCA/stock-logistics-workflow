# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

from datetime import datetime

# No current inventory, create a new one
if not terminal.tmp_val1:
    stock_inventory_obj = pool.get('stock.inventory')
    stock_inventory_id = stock_inventory_obj.create(cr, uid, {
        'name': '%s : %s' % (terminal.code, datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
    }, context=context)
    terminal.write({'tmp_val1': stock_inventory_id}, context=context)
elif tracer == 'location' and terminal.tmp_val2:
    stock_location_obj = pool.get('stock.location')
    stock_inventory_line_obj = pool.get('stock.inventory.line')

    stock_inventory_id = int(terminal.tmp_val1)
    default_code = terminal.tmp_val2
    quantity = float(terminal.tmp_val3)
    location_id = stock_location_obj.name_search(cr, uid, message, operator='=', context=context)[0][0]

    product_id = model.search(cr, uid, [('default_code', '=', default_code)], context=context)[0]
    product = model.browse(cr, uid, product_id, context=context)

    stock_inventory_line_obj.create(cr, uid, {
        'inventory_id': stock_inventory_id,
        'product_id': product_id,
        'product_uom': product.uom_id.id,
        'product_qty': quantity,
        'location_id': location_id,
    }, context=context)

    terminal.write({'tmp_val2': '', 'tmp_val3': ''}, context=context)

act = 'T'
res = [
    'Product code ?',
]
