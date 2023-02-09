from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PadronA5Config(models.Model):
    _name = 'padron.a5.config'
    _description = "Configuration for Padron A5"

    name = fields.Char('Name', size=64, required=True)
    company_id = fields.Many2one('res.company', 'Company Name', required=True)
    cuit = fields.Char(related='company_id.partner_id.vat', string='Cuit')
    wsaa_ticket_id = fields.Many2one('wsaa.ta', 'Ticket Access')


    @api.model
    def create(self, vals):
        # Creamos tambien un TA para este servcio y esta compania
        ta_obj = self.env['wsaa.ta']
        wsaa_obj = self.env['wsaa.config']
        service_obj = self.env['afipws.service']

        # Buscamos primero el wsaa que corresponde a esta compania
        # porque hay que recordar que son unicos por compania
        wsaa = wsaa_obj.search([('company_id', '=', vals['company_id'])])
        service = service_obj.search([('name', '=', 'ws_sr_padron_a5')])
        print("entroooo")
        if wsaa:
            ta_vals = {
                'name': service.id,
                'company_id': vals['company_id'],
                'config_id': wsaa.id,
            }

            ta = ta_obj.create(ta_vals)
            vals['wsaa_ticket_id'] = ta.id

        return super(PadronA5Config, self).create(vals)

    @api.multi
    def unlink(self):
        for PadronA5_conf in self:
            PadronA5_conf.wsaa_ticket_id.unlink()
        res = super(PadronA5Config, self).unlink()
        return res

