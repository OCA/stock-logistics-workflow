# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

act = 'M'
res = [
    _('|Introduction'),
    '',
    _('Welcome on the stock_scanner module.'),
    '',
    _('This scenario will explain all step types.'),
    # '',
    # _('All step types allow scrolling, if the displayed text doesn\'t fit on the screen.'),
    # _('To scroll, simply use the arrow keys.'),
    # '',
    # _('For \'List\' steps, the scrolling is horizontal, because the vertical moves are used to choose the value.'),
    # _('For all other types of steps, the scrolling is vertical.'),
]
