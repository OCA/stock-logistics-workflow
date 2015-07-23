# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

act = 'F'
res = [
    'Return values of a step',
    '',
    'All steps must return three values :',
    '- act : Type of step',
    '- res : Content to display',
    '- val : Default value',
    '',
    'The \'act\' variable must be a single character string.',
    '',
    'The \'res\' variable can contain multiple values :',
    '- A list of strings (all step types). Each string corresponds to a line of text to display. The long lines will be splitted automatically to fit on screen.',
    '- A list of tuples of two strings (list steps). The first value of each tuple is the returned value, the second value is the displayed value.',
    '- A dict of strings (list step). The key is the returned value, the second value is the displayed value.',
    '',
    'The \'val\' variable can contain multiple values :',
    '- A single value (all step types). The type of the value depends on the type of step (float, integer, boolean...).',
    '- A dict (text input step). The key \'default\' is the default value, the key \'size\' is the maximum size before automatic validation.',
]
