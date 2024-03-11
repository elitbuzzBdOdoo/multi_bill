from odoo import fields, models, api


class MultiBill(models.Model):
    _name = 'bill.multi'
    _description = 'Multi Bill Payment'
    _inherit = ['mail.thread']
    _rec_name = 'multi_bill_id'

    multi_bill_id = fields.Char(string="Multi Bill ID", readonly=True)
    vendor_name = fields.Many2one('res.partner', string="Vendor", tracking=True)
    payment_method = fields.Many2one('account.journal', string="Payment Method", required=True)
    company_name = fields.Many2one('res.partner', string="Company")
    payment_amount = fields.Float(string="Payment Amount", required=True, tracking=True)
    total_due = fields.Float(string="Total Due", compute='_compute_total_due', store=True, readonly=True)
    cash_balance = fields.Float(string="Current Cash Balance", readonly=True)
    note = fields.Char(string="Note")
    state = fields.Selection([('awaiting', 'Awaiting'), ('paid', 'Paid'), ('cancel', 'Cancel')], default='awaiting')
    payment_date = fields.Date(string="Payment Date", default=fields.Date.today)

    @api.model
    def create(self, vals):
        records = super(MultiBill, self).create(vals)
        for record in records:
            record.multi_bill_id = self.env['ir.sequence'].next_by_code('bill.multi')
        return records

    @api.depends('payment_amount', 'vendor_name')
    def _compute_total_due(self):
        for record in self:
            total_due = 0.0
            if record.vendor_name:
                purchase_orders = self.env['purchase.order'].search([
                    ('partner_id', '=', record.vendor_name.id),
                    ('state', '=', 'purchase')
                ])
                for order in purchase_orders:
                    total_due += order.amount_total - sum(payment.amount for payment in order.invoice_ids)
            record.total_due = total_due - record.payment_amount

    def bill_multi_validate(self):
        self.state = 'paid'

    def bill_multi_cancel(self):
        self.state = 'cancel'
