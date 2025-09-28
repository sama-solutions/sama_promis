# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SamaPromisContractTemplate(models.Model):
    _name = 'sama.promis.contract.template'
    _description = 'Modèle de Contrat SAMA PROMIS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Nom du Modèle", required=True, tracking=True)
    description = fields.Text(string="Description")
    
    # Template Content
    html_content = fields.Html(string="Contenu HTML", required=True,
                              help="Utilisez des variables comme {{ project.name }}, {{ partner.name }}, etc.")
    
    # Template Type
    template_type = fields.Selection([
        ('grant', 'Subvention'),
        ('service', 'Prestation de Service'),
        ('partnership', 'Partenariat'),
        ('other', 'Autre'),
    ], string="Type de Contrat", required=True, tracking=True)
    
    # Status
    active = fields.Boolean(string="Actif", default=True, tracking=True)
    
    # Usage tracking
    contract_ids = fields.One2many('sama.promis.contract', 'contract_template_id',
                                  string="Contrats Utilisant ce Modèle")
    usage_count = fields.Integer(string="Nombre d'Utilisations", 
                                compute='_compute_usage_count')
    
    # Variables disponibles
    available_variables = fields.Text(string="Variables Disponibles", 
                                    default="""Variables disponibles:
{{ project.name }} - Nom du projet
{{ project.total_budget }} - Budget total
{{ project.start_date }} - Date de début
{{ project.end_date }} - Date de fin
{{ partner.name }} - Nom du bénéficiaire
{{ partner.email }} - Email du bénéficiaire
{{ partner.phone }} - Téléphone du bénéficiaire
{{ contract.amount }} - Montant du contrat
{{ contract.start_date }} - Date de début du contrat
{{ contract.end_date }} - Date de fin du contrat
{{ today }} - Date d'aujourd'hui
{{ user.name }} - Nom de l'utilisateur actuel""",
                                    readonly=True)
    
    @api.depends('contract_ids')
    def _compute_usage_count(self):
        """Compute how many times this template has been used"""
        for template in self:
            template.usage_count = len(template.contract_ids)
    
    def action_preview_template(self):
        """Preview the template with sample data - temporarily disabled"""
        self.ensure_one()
        
        # Temporarily return a simple notification instead of using the preview model
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Aperçu Temporairement Indisponible'),
                'message': _('La fonctionnalité d\'aperçu sera disponible après la mise à jour du module.'),
                'type': 'warning',
            }
        }
    
    def action_duplicate_template(self):
        """Duplicate this template"""
        self.ensure_one()
        copy_name = _("%s (Copie)") % self.name
        self.copy({'name': copy_name})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Modèle Dupliqué'),
                'message': _('Le modèle a été dupliqué avec succès.'),
                'type': 'success',
            }
        }


# Temporarily commented out to resolve upgrade issues
# Will be re-enabled after successful module upgrade

# class SamaPromisContractTemplatePreview(models.Model):
#     _name = 'sama.promis.contract.template.preview'
#     _description = 'Aperçu du Modèle de Contrat'
#     _rec_name = 'template_id'
#     _order = 'create_date desc'
#     
#     template_id = fields.Many2one('sama.promis.contract.template', string="Modèle de Contrat", required=True)
#     preview_content = fields.Html(string="Aperçu du Contenu", readonly=True)
#     create_date = fields.Datetime(string="Date de Création", readonly=True)
#     create_uid = fields.Many2one('res.users', string="Créé par", readonly=True)
#     
#     @api.onchange('template_id')
#     def _onchange_template_id(self):
#         if self.template_id:
#             content = self.template_id.html_content
#             sample_replacements = {
#                 '{{ project.name }}': 'Projet d\'Exemple',
#                 '{{ project.total_budget }}': '100,000 €',
#                 '{{ project.start_date }}': '01/01/2024',
#                 '{{ project.end_date }}': '31/12/2024',
#                 '{{ partner.name }}': 'Organisation Bénéficiaire',
#                 '{{ partner.email }}': 'contact@organisation.com',
#                 '{{ partner.phone }}': '+221 33 123 45 67',
#                 '{{ contract.amount }}': '75,000 €',
#                 '{{ contract.start_date }}': '15/01/2024',
#                 '{{ contract.end_date }}': '15/12/2024',
#                 '{{ today }}': fields.Date.today().strftime('%d/%m/%Y'),
#                 '{{ user.name }}': self.env.user.name,
#                 '{{ payment_schedule_table }}': '<table class="table"><tr><td>Échéancier d\'exemple</td></tr></table>',
#             }
#             
#             for variable, value in sample_replacements.items():
#                 content = content.replace(variable, value)
#             
#             self.preview_content = content
#     
#     @api.model
#     def create(self, vals):
#         """Override create to cleanup old preview records"""
#         # Clean up old preview records (keep only last 10 per template)
#         if 'template_id' in vals:
#             old_previews = self.search([
#                 ('template_id', '=', vals['template_id'])
#             ], order='create_date desc', offset=10)
#             old_previews.unlink()
#         
#         return super().create(vals)

