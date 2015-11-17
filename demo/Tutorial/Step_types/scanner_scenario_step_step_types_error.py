# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

act = 'E'
res = [
    _('|Error step'),
    '',
    _('This step shows an error message, using the error colors defined in the hardware configuration.'),
    '',
    _('After this step, the scenario automatically goes back if the returned value is set to True.'),
]
val = True
