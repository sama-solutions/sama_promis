from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    ministry_id = fields.Many2one('government.ministry', string="Ministère")
