# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

terminal.write({'tmp_val3': message})

product = model.search([('default_code', '=', terminal.tmp_val2)])[0]

act = 'T'
res = [
    'Product : [%s] %s' % (product.default_code, product.name),
    'Quantity : %g %s' % (float(message), product.uom_id.name),
    '',
    'Location ?',
]
