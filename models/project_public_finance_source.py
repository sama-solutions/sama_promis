from odoo import models, fields, api

class ProjectPublicFinanceSource(models.Model):
    _name = 'project.public.finance.source'
    _description = 'Source de Financement du Projet'
    _order = 'type_source, nom_source'

    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    type_source = fields.Selection([
        ('budget_etat', 'Budget de l\'État'),
        ('partenaire_technique', 'Partenaire Technique et Financier'),
        ('prive', 'Secteur Privé'),
        ('collectivite', 'Collectivité Territoriale'),
        ('autre', 'Autre')
    ], string='Type de Source', required=True)
    nom_source = fields.Char(string='Nom de la Source', required=True)
    montant_prevu = fields.Monetary(string='Montant Prévu', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id, required=True)
    ligne_budgetaire_associee = fields.Char(string='Ligne Budgétaire Associée')
    accord_reference = fields.Char(string='Référence Accord/Convention')
    statut_financement = fields.Selection([
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours de négociation'),
        ('conditionnel', 'Conditionnel')
    ], string='Statut du Financement', default='en_cours')
    
    notes = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('unique_source_project', 'unique(project_id, nom_source)', 'Une source de financement ne peut être définie qu\'une seule fois par projet.')
    ]
