from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GovernmentProjectWizard(models.TransientModel):
    _name = 'government.project.wizard'
    _description = 'Assistant de Création de Projet Gouvernemental'
    
    # Projet Odoo source
    odoo_project_id = fields.Many2one(
        'project.project',
        string="Projet Odoo",
        required=True,
        readonly=True
    )
    
    # Informations du nouveau projet gouvernemental
    name = fields.Char(
        string="Nom du Projet",
        required=True
    )
    
    description = fields.Text(
        string="Description"
    )
    
    start_date = fields.Date(
        string="Date de Début"
    )
    
    end_date = fields.Date(
        string="Date de Fin"
    )
    
    strategic_objective_id = fields.Many2one(
        'strategic.objective',
        string="Objectif Stratégique",
        required=True,
        help="Objectif stratégique du Plan Sénégal 2050"
    )
    
    ministry_id = fields.Many2one(
        'government.ministry',
        string="Ministère Responsable",
        required=True
    )
    
    budget_id = fields.Many2one(
        'government.budget',
        string="Budget Alloué"
    )
    
    manager_id = fields.Many2one(
        'res.users',
        string="Chef de Projet"
    )
    
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Importante'),
        ('2', 'Urgente'),
        ('3', 'Critique')
    ], string="Priorité", default='0')
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Vérifie la cohérence des dates"""
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début."))
    
    def action_create_government_project(self):
        """Crée le projet gouvernemental et établit la liaison"""
        self.ensure_one()
        
        # Créer le projet gouvernemental
        gov_project_vals = {
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'strategic_objective_id': self.strategic_objective_id.id,
            'ministry_id': self.ministry_id.id,
            'budget_id': self.budget_id.id if self.budget_id else False,
            'manager_id': self.manager_id.id if self.manager_id else False,
            'priority': self.priority,
            'odoo_project_id': self.odoo_project_id.id,
        }
        
        gov_project = self.env['government.project'].create(gov_project_vals)
        
        # Mettre à jour le projet Odoo avec la référence gouvernementale
        self.odoo_project_id.write({
            'government_project_id': gov_project.id,
            'name': f"[{gov_project.project_code}] {self.name}"
        })
        
        # Retourner l'action pour ouvrir le projet gouvernemental créé
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projet Gouvernemental - {gov_project.project_code}',
            'res_model': 'government.project',
            'res_id': gov_project.id,
            'view_mode': 'form',
            'target': 'current',
        }
