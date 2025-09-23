# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SamaPromisPaymentRequest(models.Model):
    _name = 'sama.promis.payment.request'
    _description = 'Payment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'
    
    # Basic Information
    name = fields.Char('Reference', readonly=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', required=True, 
                               domain="[('state', 'in', ['approved', 'in_progress'])]")
    contract_id = fields.Many2one('sama.promis.contract', 
                                domain="[('project_id', '=', project_id)]")
    
    # Status and Dates
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ], default='draft', tracking=True)
    
    request_date = fields.Date(default=fields.Date.today, required=True)
    payment_date = fields.Date('Payment Date', readonly=True)
    
    # Financial Information
    amount = fields.Monetary(required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', 
                                default=lambda self: self.env.company.currency_id)
    
    # Relations
    partner_id = fields.Many2one('res.partner', related='project_id.partner_id',
                               store=True, readonly=True)
    user_id = fields.Many2one('res.users', 'Requested By',
                            default=lambda self: self.env.user, readonly=True)
    rejection_reason = fields.Text('Rejection Reason', readonly=True, tracking=True)
    
    # Methods
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sama.promis.payment.request')
        return super().create(vals_list)
    
    def action_submit(self):
        self.write({'state': 'submitted'})
        self._notify_approvers()
    
    def action_approve(self):
        self.write({'state': 'approved'})
        self._create_account_payment()
    
    def action_reject(self):
        return {
            'name': _('Rejection Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'sama.promis.payment.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_payment_id': self.id}
        }
    
    def _notify_approvers(self):
        # Implementation for notifying approvers
        pass
    
    def _create_account_payment(self):
        # Implementation for creating account payment
        pass
