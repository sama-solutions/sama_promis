from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectPublicProcurement(models.Model):
    _name = 'project.public.procurement'
    _description = 'Marché Public Associé au Projet'
    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    nom_marche = fields.Char(string='Nom du Marché', required=True)
    type_marche = fields.Selection([
        ('travaux', 'Travaux'),
        ('fournitures', 'Fournitures'),
        ('services', 'Services'),
        ('prestations_intellectuelles', 'Prestations Intellectuelles')
    ], string='Type de Marché', required=True)
    mode_passation = fields.Selection([
        ('appel_offres_ouvert', 'Appel d\'Offres Ouvert'),
        ('appel_offres_restreint', 'Appel d\'Offres Restreint'),
        ('entente_directe', 'Entente Directe'),
        ('demande_cotation', 'Demande de Cotation'),
        ('concours', 'Concours')
    ], string='Mode de Passation', required=True)
    montant_estime = fields.Monetary(string='Montant Estimé', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)
    date_lancement_prevue = fields.Date(string='Date Lancement Prévue')
    duree_execution_prevue = fields.Integer(string='Durée Exécution Prévue (jours)')
    criteres_selection = fields.Text(string='Critères de Sélection')
    
    @api.constrains('montant_estime')
    def _check_montant_positif(self):
        for rec in self:
            if rec.montant_estime <= 0:
                raise ValidationError("Le montant estimé doit être positif.")

