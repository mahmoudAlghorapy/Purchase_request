from odoo import models, fields, api


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'purchase.request.line'
    _rec_name = 'product_id'

    order_id = fields.Many2one('purchase.request')
    product_id = fields.Many2one('product.product', required=True, string='Product')
    description = fields.Char(string='description', related='product_id.name', readonly=False)
    quantity = fields.Float(string='Quantity', default=True)
    cost_price = fields.Float(string='Cost Price', related='product_id.standard_price', readonly=False)
    total = fields.Float(string='Total ', readonly=1, compute='_compute_total')

    @api.depends('quantity', 'cost_price')
    def _compute_total(self):
        for rec in self:
            if not rec.quantity:
                rec.total = 0
            else:
                rec.total = rec.quantity*rec.cost_price




