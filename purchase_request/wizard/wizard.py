from odoo import models, api, fields


class Rejection_reason(models.Model):
    _name = 'rejection_reason.wizard'
    _description = 'rejection_reason'

    request_id = fields.Many2one(comodel_name="purchase.request", string="Purchase request")
    rejection_reason = fields.Text(required=True, string='Rejection Reason')

    def confirm(self):
        self.request_id.rejection_reason = self.rejection_reason
        self.request_id.state = 'reject'
