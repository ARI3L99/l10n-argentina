from odoo import models, fields
from odoo.exceptions import ValidationError

class GeneralPadron(models.Model):
    _name = 'general.padron'

    padron_name = fields.Selection([
    ('arba', 'ARBA'),
    ('agip', 'AGIP'),
    ('agip_rp', 'AGIP_RP'),
    ('santa_fe', 'SANTA_FE'),
    ('jujuy', 'JUJUY'),
    ('cordoba', 'CORDOBA'),
    ('tucuman', 'TUCUMAN'),
    ('formosa', 'FORMOSA'),
],string='Padron name')
    from_date = fields.Date('From date')
    to_date = fields.Date('To date')
    vat = fields.Char('Afip code', size=15, index=1)
    percentage_perception = fields.Float('Percentage of perception')
    percentage_retention = fields.Float('Percentage of retention')
    multilateral = fields.Boolean('Is multilateral?')
    name_partner = fields.Text('Company name')
    group_retention_id = fields.Many2one(
        'agip.retention.group', 'Retention Group')
    group_perception_id = fields.Many2one(
        'agip.perception.group', 'Perception Group')
    coeficiente = fields.Float("Coeficiente")
    
    denomination = fields.Text('Denomination')
    period = fields.Char('Period')
    category = fields.Char('Category', size=20)
    category_description = fields.Char('Category description', size=18)
    ac_ret_28_97 = fields.Float('Alicuota retention rg 28 97', size=6)#cambiar para que sea igual a percetage retencion
    ac_per_23_14 = fields.Float('Alicuota perception rg 23 14', size=6)
    date_ret_28_97 = fields.Date('Date retention rg 28 97')
    date_per_23_14 = fields.Date('Date perception rg 23 14')
    ac_per_33_99 = fields.Float('Alicuota perception rg 33 99', size=6)
    ac_per_27_00 = fields.Float('Alicuota perception rg 27 00', size=6)
    date_per_33_99 = fields.Date('Date perception rg 33 99')
    date_per_27_00 = fields.Date('Date perception rg 27 00')
    regime = fields.Text('Regime')
    exent = fields.Boolean('Exent')