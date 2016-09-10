# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

act = 'F'
res = [
    _('Return values of a step'),
    '',
    _('All steps must return three values :'),
    _('- act : Type of step'),
    _('- res : Content to display'),
    _('- val : Default value'),
    '',
    _('The \'act\' variable must be a single character string.'),
    '',
    _('The \'res\' variable can contain multiple values :'),
    _('- A list of strings (all step types). Each string corresponds to a line of text to display. The long lines will be splitted automatically to fit on screen.'),
    _('- A list of tuples of two strings (list steps). The first value of each tuple is the returned value, the second value is the displayed value.'),
    _('- A dict of strings (list step). The key is the returned value, the second value is the displayed value.'),
    '',
    _('The \'val\' variable can contain multiple values :'),
    _('- A single value (all step types). The type of the value depends on the type of step (float, integer, boolean...).'),
    _('- A dict (text input step). The key \'default\' is the default value, the key \'size\' is the maximum size before automatic validation.'),
]
