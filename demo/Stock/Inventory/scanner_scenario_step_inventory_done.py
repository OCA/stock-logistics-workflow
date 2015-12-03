# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

stock_inventory = env['stock.inventory'].browse(int(terminal.tmp_val1))
stock_inventory.prepare_inventory()
stock_inventory.action_done()

act = 'F'
res = [
    _('Inventory done !'),
]
