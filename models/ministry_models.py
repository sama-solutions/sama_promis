from odoo import models, fields

class GovernmentMinistry(models.Model):
    _name = 'government.ministry'
    _description = 'Ministère Gouvernemental'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom du Ministère", required=True, tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string="Code du Ministère", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    type = fields.Selection([
        ('presidency', 'Présidence'),
        ('ministry', 'Ministère'),
        ('secretariat', "Secrétariat d'État"),
        ('agency', 'Agence'),
    ], string="Type", default='ministry', required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)
    
    # Informations de contact
    address = fields.Text(string="Adresse", readonly=True, states={'draft': [('readonly', False)]})
    phone = fields.Char(string="Téléphone", readonly=True, states={'draft': [('readonly', False)]})
    email = fields.Char(string="Email", readonly=True, states={'draft': [('readonly', False)]})
    website = fields.Char(string="Site Web", readonly=True, states={'draft': [('readonly', False)]})
    
    # Relations
    project_ids = fields.One2many('government.project', 'ministry_id', string="Projets")
    budget_ids = fields.One2many('government.budget', 'ministry_id', string="Budgets")
    decision_ids = fields.One2many('government.decision', 'ministry_id', string="Décisions")
    event_ids = fields.One2many('government.event', 'organizer_id', string="Événements Organisés")
    
    # Statistiques
    project_count = fields.Integer(string="Nombre de Projets", compute='_compute_project_count')
    
    def _compute_project_count(self):
        """Calcule le nombre de projets du ministère"""
        for ministry in self:
            ministry.project_count = len(ministry.project_ids)

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})
    
    def action_view_projects(self):
        """Action pour voir tous les projets du ministère"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projets - {self.name}',
            'res_model': 'government.project',
            'view_mode': 'tree,form,kanban',
            'domain': [('ministry_id', '=', self.id)],
            'context': {
                'default_ministry_id': self.id,
                'search_default_ministry_id': self.id,
            },
            'target': 'current',
        }
    
    def get_public_url(self):
        """Retourne l'URL publique du ministère"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/senegal2050/ministry/{self.id}"
    
    def get_qr_code_url(self):
        """Retourne l'URL pour générer le QR code du ministère"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/senegal2050/qr/government.ministry/{self.id}"
    
    def action_share_public(self):
        """Action pour partager publiquement le ministère"""
        self.ensure_one()
        public_url = self.get_public_url()
        return {
            'type': 'ir.actions.act_url',
            'url': public_url,
            'target': 'new',
        }
