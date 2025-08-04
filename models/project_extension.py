from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectProjectExtension(models.Model):
    """Extension du modèle projet d'Odoo pour le Plan Sénégal 2050"""
    _inherit = 'project.project'
    
    # Lien vers le projet gouvernemental
    government_project_id = fields.Many2one(
        'government.project',
        string="Projet Gouvernemental SN-2050",
        help="Projet gouvernemental associé dans le cadre du Plan Sénégal 2050"
    )
    
    # Champs pour affichage
    government_project_code = fields.Char(
        related='government_project_id.project_code',
        string="Code SN-2050",
        readonly=True,
        store=True
    )
    
    is_government_project = fields.Boolean(
        string="Projet Gouvernemental",
        compute='_compute_is_government_project',
        store=True
    )
    
    # Informations stratégiques
    strategic_objective_id = fields.Many2one(
        'strategic.objective',
        related='government_project_id.strategic_objective_id',
        string="Objectif Stratégique",
        readonly=True,
        store=True
    )
    
    ministry_id = fields.Many2one(
        'government.ministry',
        related='government_project_id.ministry_id',
        string="Ministère Responsable",
        readonly=True,
        store=True
    )
    
    government_budget_id = fields.Many2one(
        'government.budget',
        related='government_project_id.budget_id',
        string="Budget Alloué",
        readonly=True,
        store=True
    )
    
    government_priority = fields.Selection(
        related='government_project_id.priority',
        string="Priorité Gouvernementale",
        readonly=True,
        store=True
    )
    
    @api.depends('government_project_id')
    def _compute_is_government_project(self):
        """Détermine si c'est un projet gouvernemental"""
        for record in self:
            record.is_government_project = bool(record.government_project_id)
    
    def write(self, vals):
        """Synchronise les modifications avec le projet gouvernemental"""
        result = super(ProjectProjectExtension, self).write(vals)
        
        # Synchroniser avec le projet gouvernemental si nécessaire
        if self.government_project_id and any(key in vals for key in ['name', 'date_start', 'date', 'user_id']):
            self._sync_to_government_project()
        
        return result
    
    def _sync_to_government_project(self):
        """Synchronise les données vers le projet gouvernemental"""
        for record in self.filtered('government_project_id'):
            gov_project = record.government_project_id
            
            # Extraire le nom sans le code
            name_without_code = record.name
            if record.government_project_code and record.name.startswith(f"[{record.government_project_code}]"):
                name_without_code = record.name.replace(f"[{record.government_project_code}] ", "")
            
            sync_vals = {}
            
            if gov_project.name != name_without_code:
                sync_vals['name'] = name_without_code
            
            if record.date_start and gov_project.start_date != record.date_start:
                sync_vals['start_date'] = record.date_start
                
            if record.date and gov_project.end_date != record.date:
                sync_vals['end_date'] = record.date
                
            if record.user_id and gov_project.manager_id != record.user_id:
                sync_vals['manager_id'] = record.user_id.id
            
            if sync_vals:
                gov_project.write(sync_vals)
    
    def action_open_government_project(self):
        """Ouvre le projet gouvernemental associé"""
        self.ensure_one()
        if not self.government_project_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projet Gouvernemental - {self.government_project_code}',
            'res_model': 'government.project',
            'res_id': self.government_project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_create_government_project(self):
        """Crée un nouveau projet gouvernemental à partir du projet Odoo"""
        self.ensure_one()
        
        if self.government_project_id:
            raise ValidationError(_("Ce projet est déjà lié à un projet gouvernemental."))
        
        # Ouvrir un wizard pour sélectionner l'objectif stratégique et le ministère
        return {
            'type': 'ir.actions.act_window',
            'name': _('Créer un Projet Gouvernemental'),
            'res_model': 'government.project.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_odoo_project_id': self.id,
                'default_name': self.name,
                'default_start_date': self.date_start,
                'default_end_date': self.date,
                'default_manager_id': self.user_id.id if self.user_id else False,
            }
        }


class ProjectTaskExtension(models.Model):
    """Extension du modèle tâche d'Odoo pour le Plan Sénégal 2050"""
    _inherit = 'project.task'
    
    # Lien vers le projet gouvernemental (via le projet)
    government_project_id = fields.Many2one(
        'government.project',
        related='project_id.government_project_id',
        string="Projet Gouvernemental SN-2050",
        readonly=True,
        store=True
    )
    
    government_project_code = fields.Char(
        related='government_project_id.project_code',
        string="Code SN-2050",
        readonly=True,
        store=True
    )
    
    strategic_objective_id = fields.Many2one(
        'strategic.objective',
        related='government_project_id.strategic_objective_id',
        string="Objectif Stratégique",
        readonly=True,
        store=True
    )
