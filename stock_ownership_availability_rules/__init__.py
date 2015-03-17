from . import model


def fill_quant_owner(cr):
    cr.execute('UPDATE stock_quant '
               'SET owner_id = res_company.partner_id '
               'FROM res_company '
               'WHERE owner_id IS NULL '
               'AND stock_quant.company_id = res_company.id;')
