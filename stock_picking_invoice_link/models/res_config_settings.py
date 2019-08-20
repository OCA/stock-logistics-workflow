from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    picking_reports_as_email_attachment = fields.Boolean(
        string="Email attachment",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            {
                'picking_reports_as_email_attachment':
                    IrDefault.get(
                        'res.config.settings',
                        'picking_reports_as_email_attachment')
            }
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set(
            'res.config.settings',
            'picking_reports_as_email_attachment',
            self.picking_reports_as_email_attachment)
        return True
