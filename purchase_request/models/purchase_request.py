# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class purchase_request(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_name = fields.Char(string='Request name', required=True)
    requested_by = fields.Many2one('res.users', string="Requested by", required=True,
                                   default=lambda self: self.env.user)
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    end_date = fields.Date(string='End Date')
    rejection_reason = fields.Text(string='Rejection Reason', readonly=False)
    order_line_id = fields.One2many(comodel_name='purchase.request.line', inverse_name='order_id',
                                    string='Order Lines')
    all_quantity_reserved = fields.Boolean(string='All Quantity Reserved', compute='reserved_qty')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price')
    state = fields.Selection([('draft', 'Draft'),
                              ('to_be_approved', 'to be approved'),
                              ('approve', 'approve'),
                              ('reject', 'reject'),
                              ('cancel', 'canceled')],
                             string='Status', tracking=True, readonly=True, default='draft')

    count_purchase_orders = fields.Integer(compute='get_history_count')

    @api.depends('order_line_id')
    def reserved_qty(self):
        for rec in self:
            confirmed_po = self.env['purchase.order'].search(
                [('request_id', '=', rec.id), ('state', '=', 'purchase')])
            qty = 0
            requested = 0
            for po in confirmed_po:
                for line in po.order_line:
                    qty += line.product_qty
                # qty += sum(line.product_qty for line in po.order_line)
            for line in rec.order_line_id:
                requested += line.quantity

            print('requested is ----->', requested)
            print('quantity--->', qty)
            if requested == qty:
                rec.all_quantity_reserved = True










    def get_history_count(self):
        count = self.env['purchase.order'].search_count([('name', '=', self.request_name)])
        self.count_purchase_orders = count

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_print(self):
        self.write({'state': "approve"})
        return self.env.ref('purchase_request.report_purchase_request').report_action(self)

    def action_create_po(self):
        line_vals = []
        for line in self.order_line_id:
            line_vals.append([0, 0, {'product_id': line.product_id.id,
                                     'product_qty': line.quantity
                                     }])
        vals = {
            'name': self.request_name,
            'partner_id': self.requested_by.id,
            'date_approve': self.start_date,
            'date_planned': self.end_date,
            'user_id': self.env.user.id,
            'amount_total': self.total_price,
            'order_line': line_vals,
            'request_id': self.id
        }
        self.env['purchase.order'].create(vals)

    def action_to_be_approved(self):
        for rec in self:
            rec.state = 'to_be_approved'

    def action_approve(self):

        for rec in self:
            full_mail = "Purchase Request (x) has been approved"
            users = self.env.ref('purchase_request.purchase_manager').users
            for user in users:
                mail_values = {
                    'auto_delete': True,
                    'author_id': self.env.user.id,
                    'email_from': self.env.user.partner_id.email_formatted,
                    'email_to': user.partner_id.email_formatted,
                    'body_html': full_mail,

                }
                rec.env['mail.mail'].sudo().create(mail_values)
            rec.state = 'approve'

    def action_reject(self):
        for rec in self:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'purchase_request.action_view_rejection_reason')

            action['context'] = {
                'default_request_id': rec.id
            }

            return action

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.depends('order_line_id')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(l.total for l in self.order_line_id)

    def preview_patient_history(self):

        return {
            'name': _('Purchase Orders'),
            'domain': [('request_id', '=', self.id)],
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }




