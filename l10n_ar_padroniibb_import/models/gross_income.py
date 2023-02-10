from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class GrossIncome(models.Model):
    _name = "gross.income"

    res_partner = fields.Many2one("res.partner")
    province_id = fields.Many2one("res.country.state", string="Provincias")
    type_taxpayer = fields.Selection([
        ('local', 'Local'),
        ('CM', 'CM'),
        ('sin_actividad','Sin Actividad')
    ],string="Tipo de contribuyente", required=True)

class res_partner(models.Model):
    _inherit = 'res.partner'

    gross_income = fields.One2many("gross.income", "res_partner")

    @api.model
    def default_get(self, fields_list):
        res = super(res_partner, self).default_get(fields_list)
        province = self.env['res.country.state'].search([('country_id', "=", 'Argentina'),('code', "in", ['W', 'P', 'N', 'Q'])]).ids

        vals = [(0, 0, {'province_id': province[0]}),
                (0, 0, {'province_id': province[1]}),
                (0, 0, {'province_id': province[2]}),
                (0, 0, {'province_id': province[3]})
                ]
        res.update({'gross_income': vals})
        return res

    @api.model
    def create(self, values):
        for rec in values.get('gross_income'):
            if not rec[-1].get('type_taxpayer'):
                raise ValidationError(_("El campo tipo de contribuyente debe ser completado"))
        res = super(res_partner, self).create(values)
        return res
