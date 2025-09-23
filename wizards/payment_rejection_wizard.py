# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PaymentRejectionWizard(models.TransientModel):
    _name = 'sama.promis.payment.rejection.wizard'
    _description = 'Payment Rejection Wizard'
    
    payment_id = fields.Many2one('sama.promis.payment.request', required=True)
    reason = fields.Text('Rejection Reason', required=True)
    
    def action_reject(self):
        self.ensure_one()
        self.payment_id.write({
            'state': 'rejected',
            'rejection_reason': self.reason
        })
        self.payment_id.message_post(
            body=_("Payment rejected. Reason: %s") % self.reason
        )
        return {'type': 'ir.actions.act_window_close'}
