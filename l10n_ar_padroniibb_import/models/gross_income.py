from odoo import models, fields


class GrossIncome(models.Model):
    _name = "gross.income"

    res_partner = fields.Many2one("res.partner")
    province_id = fields.Many2one("res.country.state", string="Provincias")
    type_taxpayer = fields.Selection([
        ('local', 'Local'),
        ('CM', 'CM')
    ],string="Tipo de contribuyente")

class res_partner(models.Model):
    _inherit = 'res.partner'

    gross_income = fields.One2many("gross.income", "res_partner")
