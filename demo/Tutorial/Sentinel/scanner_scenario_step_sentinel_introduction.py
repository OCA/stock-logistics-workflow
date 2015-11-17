# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

act = 'M'
res = [
    _('Introduction'),
    '',
    _('This scenario will explain some features of the sentinel ncurses client.'),
    '',
    _('This client is specific to the stock_scanner module.'),
]
