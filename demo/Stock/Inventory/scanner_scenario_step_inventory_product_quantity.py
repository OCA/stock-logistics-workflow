# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

terminal.write({'tmp_val2': message})

product = model.search([('default_code', '=', message)])

act = 'Q'
res = [
    _('Product : [%s] %s') % (product.default_code, product.name),
    _('UoM : %s') % product.uom_id.name,
    '',
    _('Select quantity'),
]
