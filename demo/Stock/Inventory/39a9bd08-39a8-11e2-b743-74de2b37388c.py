# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

terminal.write({'tmp_val3': message}, context=context)

product_id = model.search(cr, uid, [('default_code', '=', terminal.tmp_val2)], context=context)[0]
product = model.browse(cr, uid, product_id, context=context)

act = 'T'
res = [
    'Product : [%s] %s' % (product.default_code, product.name),
    'Quantity : %g %s' % (float(message), product.uom_id.name),
    '',
    'Location ?',
]
