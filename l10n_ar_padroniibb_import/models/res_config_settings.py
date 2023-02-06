from odoo import api, models, fields
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta


from datetime import datetime

import time


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    patterns_keep = fields.Selection([
        ('1', '1'),('2', '2'),
        ('3', '3'),('4', '4'),
        ('5', '5'),('6', '6'),
        ('7', '7'),('8', '8'),
        ('9', '9'),('10', '10')
        ],string="patterns to keep",config_parameter="account.patterns_keep")

    @api.onchange('patterns_keep')
    def onchange_patterns_keep(self):
        date = datetime.today() - relativedelta(months=int(self.patterns_keep), day=1)

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSetting, self).get_values()
    #     param = self.env['ir.config_parameter'].sudo()
    #     patterns_keep = int(
    #         param.get_param('account.patterns_keep'))
    #     res.update(patterns_keep=patterns_keep)
    #     return res

    @api.multi
    def set_values(self):
        super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'account.patterns_keep',
            self.patterns_keep)













