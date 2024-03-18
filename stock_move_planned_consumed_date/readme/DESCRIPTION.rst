This module avoid to merge stock.move with different planned consumed date.

This module by itself won't set the value on stock.move, you have to alter the way
procurement are created to inject the expected consumed date base on your requirements.

This is useful when you have big or multiple warehouse and you want to apply business
reservation rule based on this planned consumed date such as short DLC.
