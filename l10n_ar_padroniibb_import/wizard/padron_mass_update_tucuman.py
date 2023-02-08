##############################################################################
#   Copyright (c) 2018 Eynes/E-MIPS (www.eynes.com.ar)
#   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PadronMassUpdateTucuman(models.TransientModel):
    _name = 'padron.mass.update.tucuman'
    _description = 'Padron Mass Update'

    tucuman_ac = fields.Boolean('Update Tucumán Contribuyentes')
    tucuman_co = fields.Boolean('Update Tucumán Coeficientes')


    # Rentencion Tucumán
    @api.model
    def _update_retention_tucuman_ac(self, retention):
        cr = self.env.cr
        cr.commit()
        query = """
        WITH padron AS (
            SELECT
                rp.id p_partner_id,
                par.percentage_perception p_percentage,
                par.multilateral p_multilateral
            FROM res_partner rp
                JOIN padron_tucuman_acreditan par ON par.vat=rp.vat
            WHERE
                rp.parent_id IS NULL
                AND rp.supplier
        ),
        retentions AS (
            SELECT
                rpr.id r_id,
                rpr.partner_id r_partner_id,
                rpr.percent r_percentage
            FROM res_partner_retention rpr
            WHERE rpr.retention_id=%s
        )
        SELECT * FROM (SELECT padron.*, retentions.*,
            CASE
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage <> r_percentage)
                    THEN 'UPDATE'  -- In padron and sys
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage = r_percentage)
                    THEN 'NONE'  -- In padron and sys but same percent
                WHEN (p_partner_id IS NOT NULL) AND
                    (r_partner_id IS NULL)
                    THEN 'CREATE'  -- In padron not in sys
                WHEN (p_partner_id IS NULL)
                    AND (r_partner_id IS NOT NULL)
                    THEN 'DELETE'  -- Not in padron but in sys
                ELSE 'ERROR' -- Never should enter here
            END umode
            FROM padron
                FULL JOIN retentions
                ON retentions.r_partner_id=padron.p_partner_id) z
        WHERE umode != 'NONE';
        """

        params = (retention.id, )
        cr.execute(query, params)

        for res in cr.fetchall():
            if res[6] == 'UPDATE':  # Change the amount of percentage
                q = """
                UPDATE res_partner_retention SET
                    percent=%(percent)s,
                    from_padron = True
                WHERE id=%(id)s
                """
                q_params = {
                    'percent': res[1],
                    'id': res[3],
                }
                self._cr.execute(q, q_params)
            elif res[6] == 'DELETE':   # Set the percentage to -1
                q = """
                UPDATE res_partner_retention SET
                    percent=%(percent)s,
                    from_padron = True
                WHERE id=%(id)s
                """
                q_params = {
                    'percent': -1,
                    'id': res[3],
                }
                self._cr.execute(q, q_params)
            elif res[6] == 'CREATE':  # Create the res.partner.retention
                q = """
                INSERT INTO res_partner_retention (
                    partner_id,
                    percent,
                    retention_id,
                    from_padron
                ) VALUES (
                    %(partner_id)s,
                    %(percent)s,
                    %(retention_id)s,
                    True
                )"""
                q_params = {
                    'percent': res[1],
                    'partner_id': res[0],
                    'retention_id': retention.id,

                }
                self._cr.execute(q, q_params)
            else:
                e_title = _('Query Error\n')
                e_msg = _('Unexpected result: %s' % str(res))
                raise ValidationError(e_title + e_msg)

    # Percepcion Tucumán
    @api.model
    def _update_perception_tucuman_ac(self, perception):
        multilateral_record = self.env.ref(
            'l10n_ar_point_of_sale.iibb_situation_multilateral')
        local_record = self.env.ref(
            'l10n_ar_point_of_sale.iibb_situation_local')
        cr = self.env.cr
        cr.commit()
        query = """
        WITH padron AS (
            SELECT
                rp.id p_partner_id,
                par.percentage_perception p_percentage,
                par.multilateral p_multilateral
            FROM res_partner rp
                JOIN padron_tucuman_acreditan par ON par.vat=rp.vat
            WHERE
                rp.parent_id IS NULL
                AND rp.customer
        ),
        perceptions AS (
            SELECT
                rpp.id r_id,
                rpp.partner_id r_partner_id,
                rpp.percent r_percentage
            FROM res_partner_perception rpp
            WHERE rpp.perception_id=%s
        )
        SELECT * FROM (SELECT padron.*, perceptions.*,
            CASE
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage <> r_percentage)
                    THEN 'UPDATE'  -- In padron and sys
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage = r_percentage)
                    THEN 'NONE'  -- In padron and sys but same percent
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NULL)
                    THEN 'CREATE'  -- In padron not in sys
                WHEN (p_partner_id IS NULL)
                    AND (r_partner_id IS NOT NULL)
                    THEN 'DELETE'  -- Not in padron but in sys
                ELSE 'ERROR' -- Never should enter here
            END umode
            FROM padron
                FULL JOIN perceptions
                ON perceptions.r_partner_id=padron.p_partner_id) z
        WHERE umode != 'NONE';
        """

        params = (perception.id, )
        cr.execute(query, params)

        for res in cr.fetchall():
            if res[6] == 'UPDATE':  # Change the amount of percentage
                q = "UPDATE res_partner_perception SET percent=%(percent)s, \
                    from_padron = True WHERE id=%(id)s"
                q_params = {'percent': res[1], 'id': res[3]}
                self._cr.execute(q, q_params)
            elif res[6] == 'DELETE':   # Set the percentage to -1
                q = "UPDATE res_partner_perception SET percent=%(percent)s, \
                    from_padron = True WHERE id=%(id)s"
                q_params = {'percent': -1, 'id': res[3]}
                self._cr.execute(q, q_params)
            elif res[6] == 'CREATE':  # Create the res.partner.perception
                q = """
                INSERT INTO res_partner_perception (
                    partner_id,
                    percent,
                    perception_id,
                    from_padron,
                    sit_iibb
                ) VALUES (
                    %(partner_id)s,
                    %(percent)s,
                    %(perception_id)s,
                    True,
                    %(sit_iibb)s
                )"""
                q_params = {
                    'percent': res[1],
                    'partner_id': res[0],
                    'perception_id': perception.id,
                    'sit_iibb': multilateral_record.id if res[2]
                    else local_record.id,
                }
                self._cr.execute(q, q_params)
            else:
                #e_title = _('Query Error\n')
                #e_msg = _('Unexpected result: %s' % str(res))
                _logger.error('ERROR with register %s' % str(res))
                # print('error')
                # raise ValidationError(e_title + e_msg)

    # Rentencion Tucumán
    @api.model
    def _update_retention_tucuman_co(self, retention):
        cr = self.env.cr
        cr.commit()
        query = """
        WITH padron AS (
            SELECT
                rp.id p_partner_id,
                par.coeficiente p_percentage,
                par.multilateral p_multilateral
            FROM res_partner rp
                JOIN padron_tucuman_coeficiente par ON par.vat=rp.vat
            WHERE
                rp.parent_id IS NULL
                AND rp.supplier
        ),
        retentions AS (
            SELECT
                rpr.id r_id,
                rpr.partner_id r_partner_id,
                rpr.percent r_percentage
            FROM res_partner_retention rpr
            WHERE rpr.retention_id=%s
        )
        SELECT * FROM (SELECT padron.*, retentions.*,
            CASE
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage <> r_percentage)
                    THEN 'UPDATE'  -- In padron and sys
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage = r_percentage)
                    THEN 'NONE'  -- In padron and sys but same percent
                WHEN (p_partner_id IS NOT NULL) AND
                    (r_partner_id IS NULL)
                    THEN 'CREATE'  -- In padron not in sys
                WHEN (p_partner_id IS NULL)
                    AND (r_partner_id IS NOT NULL)
                    THEN 'DELETE'  -- Not in padron but in sys
                ELSE 'ERROR' -- Never should enter here
            END umode
            FROM padron
                FULL JOIN retentions
                ON retentions.r_partner_id=padron.p_partner_id) z
        WHERE umode != 'NONE';
        """

        params = (retention.id, )
        cr.execute(query, params)

        for res in cr.fetchall():
            if res[6] == 'UPDATE':  # Change the amount of percentage
                q = """
                UPDATE res_partner_retention SET
                    percent=%(percent)s,
                    from_padron = True
                WHERE id=%(id)s
                """
                q_params = {
                    'percent': res[1],
                    'id': res[3],
                }
                self._cr.execute(q, q_params)
            elif res[6] == 'DELETE':   # Set the percentage to -1
                q = """
                UPDATE res_partner_retention SET
                    percent=%(percent)s,
                    from_padron = True
                WHERE id=%(id)s
                """
                q_params = {
                    'percent': -1,
                    'id': res[3],
                }
                self._cr.execute(q, q_params)
            elif res[6] == 'CREATE':  # Create the res.partner.retention
                q = """
                INSERT INTO res_partner_retention (
                    partner_id,
                    percent,
                    retention_id,
                    from_padron
                ) VALUES (
                    %(partner_id)s,
                    %(percent)s,
                    %(retention_id)s,
                    True
                )"""
                q_params = {
                    'percent': res[1],
                    'partner_id': res[0],
                    'retention_id': retention.id,

                }
                self._cr.execute(q, q_params)
            else:
                e_title = _('Query Error\n')
                e_msg = _('Unexpected result: %s' % str(res))
                raise ValidationError(e_title + e_msg)

    # Percepcion Tucumán
    @api.model
    def _update_perception_tucuman_co(self, perception):
        cr = self.env.cr
        cr.commit()
        query = """
        WITH padron AS (
            SELECT
                rp.id p_partner_id,
                par.coeficiente p_percentage,
                par.multilateral p_multilateral
            FROM res_partner rp
                JOIN padron_tucuman_coeficiente par ON par.vat=rp.vat
            WHERE
                rp.parent_id IS NULL
                AND rp.customer
        ),
        perceptions AS (
            SELECT
                rpp.id r_id,
                rpp.partner_id r_partner_id,
                rpp.percent r_percentage
            FROM res_partner_perception rpp
            WHERE rpp.perception_id=%s
        )
        SELECT * FROM (SELECT padron.*, perceptions.*,
            CASE
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage <> r_percentage)
                    THEN 'UPDATE'  -- In padron and sys
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NOT NULL)
                    AND (p_percentage = r_percentage)
                    THEN 'NONE'  -- In padron and sys but same percent
                WHEN (p_partner_id IS NOT NULL)
                    AND (r_partner_id IS NULL)
                    THEN 'CREATE'  -- In padron not in sys
                WHEN (p_partner_id IS NULL)
                    AND (r_partner_id IS NOT NULL)
                    THEN 'DELETE'  -- Not in padron but in sys
                ELSE 'ERROR' -- Never should enter here
            END umode
            FROM padron
                FULL JOIN perceptions
                ON perceptions.r_partner_id=padron.p_partner_id) z
        WHERE umode != 'NONE';
        """

        params = (perception.id, )
        cr.execute(query, params)

        for res in cr.fetchall():
            if res[6] == 'UPDATE':  # Change the amount of percentage
                q = "UPDATE res_partner_perception SET percent=%(percent)s, \
                    from_padron = True WHERE id=%(id)s"
                q_params = {'percent': res[1], 'id': res[3]}
                self._cr.execute(q, q_params)
            elif res[6] == 'DELETE':   # Set the percentage to -1
                q = "UPDATE res_partner_perception SET percent=%(percent)s, \
                    from_padron = True WHERE id=%(id)s"
                q_params = {'percent': -1, 'id': res[3]}
                self._cr.execute(q, q_params)
            elif res[6] == 'CREATE':  # Create the res.partner.perception
                q = """
                INSERT INTO res_partner_perception (
                    partner_id,
                    percent,
                    perception_id,
                    from_padron
                ) VALUES (
                    %(partner_id)s,
                    %(percent)s,
                    %(perception_id)s,
                    True
                )"""
                q_params = {
                    'percent': res[1],
                    'partner_id': res[0],
                    'perception_id': perception.id,

                }
                self._cr.execute(q, q_params)
            else:
                #e_title = _('Query Error\n')
                #e_msg = _('Unexpected result: %s' % str(res))
                _logger.error('ERROR with register %s' % str(res))
                # print('error')
                # raise ValidationError(e_title + e_msg)



    @api.multi
    def action_update_tucuman_ac(self):
        perception_obj = self.env['perception.perception']
        retention_obj = self.env['retention.retention']

        if self.tucuman_ac:
            # Actualizamos Percepciones
            percep_tucuman_ac = perception_obj._get_perception_from_tucuman_ac()
            if not percep_tucuman_ac:
                raise ValidationError(
                    _("Perception Error!\n") +
                    _("There is no perception configured to update " +
                      "from Padron Tucumán"))
            self._update_perception_tucuman_ac(percep_tucuman_ac[0])
            # Actualizamos Retenciones
            retent_tucuman_ac = retention_obj._get_retention_from_tucuman()
            if not retent_tucuman_ac:
                raise ValidationError(
                    _("Retention Error!\n") +
                    _("There is no retention configured to update " +
                      "from Padron Tucumán"))
            self._update_retention_tucuman_ac(retent_tucuman_ac[0])

    @api.multi
    def action_update_tucuman_co(self):
        perception_obj = self.env['perception.perception']
        retention_obj = self.env['retention.retention']
        if self.tucuman_co:
            # Actualizamos Percepciones
            percep_tucuman_co = perception_obj._get_perception_from_tucuman_co()
            if not percep_tucuman_co:
                raise ValidationError(
                    _("Perception Error!\n") +
                    _("There is no perception configured to update " +
                      "from Padron Tucumán"))
            self._update_perception_tucuman_co(percep_tucuman_co[0])
            # Actualizamos Retenciones
            retent_tucuman_co = retention_obj._get_retention_from_tucuman()
            if not retent_tucuman_co:
                raise ValidationError(
                    _("Retention Error!\n") +
                    _("There is no retention configured to update " +
                      "from Padron Tucuman"))
            self._update_retention_tucuman_co(retent_tucuman_co[0])
