This module restricts the reuse of disposable packages by not allowing to select them in stock
move lines after they have already been allocated in a delivery.

This restriction can be activated or deactivated at package type level. So the user can select
for each package type if the disposable packages can be reused or not.

Note: This module will be incompatible with any module that modifies the stock.move.line package_id
or result_package_id fields domain.
