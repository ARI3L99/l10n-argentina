##############################################################################
#   Copyright (c) 2018 Eynes/E-MIPS (www.eynes.com.ar)
#   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from odoo import models, fields, api


class ResCity(models.Model):
    _name = 'res.city'
    _inherit = 'res.city'
    _description = 'Cities'

    @api.multi
    def name_get(self):
        ret = []
        for city in self:
            if city.state_id:
                ret.append((city.id, "%s (%s)" % (city.name,
                                                  city.state_id.name or '')))
            else:
                ret.append((city.id, city.name))

        return ret

    @api.onchange("state_id")
    def onchange_state_id(self):
        if self.state_id and self.country_id != self.state_id.country_id:
            self.country_id = self.state_id.country_id and \
                self.state_id.country_id.id

    def default_country_id(self):
        return self.env.ref("base.ar").id

    afip_code = fields.Char(string='AFIP Code', size=16)
    country_id = fields.Many2one(
        'res.country', string='Country', default=default_country_id)
