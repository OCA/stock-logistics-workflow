# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CannabisStrain(models.Model):

    _name = 'cannabis.strain'
    _description = 'Cannabis Strain'

    code = fields.Char()
    name = fields.Char(
        required=True,
    )
    mother_id = fields.Many2one(
        string='Mother',
        comodel_name='cannabis.strain',
        help='The mother plant produced the flowers.',
    )
    father_id = fields.Many2one(
        string='Father',
        comodel_name='cannabis.strain',
        help='The father plant pollinated the flowers.',
    )
    lineage_ids = fields.Many2many(
        string='Lineage',
        comodel_name='cannabis.strain',
        help='The true parental lineage is not known, but this strain is a '
             'known descendant of these.',
    )
    child_ids = fields.Many2many(
        string='Children',
        comodel_name=_name,
        compute='_compute_child_ids',
    )

    @api.multi
    def _compute_child_ids(self):
        for record in self:
            record.child_ids = self.search([
                ('parent_ids', 'in', self.ids),
            ])

    @api.multi
    @api.constrains('father_id', 'mother_id', 'lineage_ids')
    def _check_mother_father_lineage(self):
        """Lineage cannot be set when the known parents are."""
        for record in self:
            if record.lineage_ids:
                if record.mother_id or record.father_id:
                    raise ValidationError(_(
                        'The mother/father cannot be set at the same time '
                        'as the lineage field. This is because the mother and '
                        'father are either known, or not.',
                    ))

    @api.multi
    def name_get(self):
        names = []
        for record in self:
            if record.lineage_ids:
                name = ' / '.join(record.lineage_ids.mapped('name'))
            else:
                name = '%s x %s' % (
                    record.mother_id.name, record.father_id.name,
                )
            names.append((record.id, name))
        return names
