from odoo import models, fields

class ProjectPublicFinanceSource(models.Model):
    _name = 'project.public.finance.source'
    _description = 'Source de Financement Projet'
    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    type_source = fields.Selection([
        ('budget_national', 'Budget National'),
        ('pret_ptf', 'Prêt PTF'),
        ('don_ptf', 'Don PTF'),
        ('fonds_propres_ct', 'Fonds Propres Collectivité Territoriale'),
        ('ppp', 'Partenariat Public-Privé'),
        ('autre', 'Autre')
    ], string='Type de Source', required=True)
    nom_source = fields.Char(string='Nom de la Source (Ex: Banque Mondiale)')
    montant_prevu = fields.Monetary(string='Montant Prévu', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)
    ligne_budgetaire_associee = fields.Char(string='Ligne Budgétaire Associée', help="Code de la ligne budgétaire. (LOLF Art. 13, 15)")
    accord_reference = fields.Char(string='Référence Accord (Prêt/Don/Délibération CT)', help="Ex: Référence de l'accord de prêt ou de la délibération de la CT.")

