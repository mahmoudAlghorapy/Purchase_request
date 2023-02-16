from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    request_id = fields.Many2one('purchase.request', ondelete='cascade')

    def button_confirm(self):
        for order in self:
            if order.request_id:
                for line in order.order_line:
                    confirmed_po = self.env['purchase.order'].search([('request_id','=', order.request_id.id), ('state','=','purchase')])
                    confirmed_qty = 0
                    for po in confirmed_po:
                        confirmed_qty += po.order_line.filtered(lambda x: x.product_id == line.product_id).product_qty


                    request_line = order.request_id.order_line_id.filtered(lambda x: x.product_id == line.product_id)
                    request_qty = request_line.quantity
                    qty = confirmed_qty + line.product_qty
                    if qty > request_qty:
                        raise ValidationError(
                            'Product Qty greater than request qty.\n'
                            'Product:  %s\n' % line.product_id.name)





            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
