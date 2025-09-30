# -*- coding: utf-8 -*-
"""
SAMA PROMIS Projects - Project Model
====================================

Modèle principal pour la gestion des projets SAMA PROMIS.
Inspiré de SAMA ETAT avec cycles de vie et boutons d'action.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class SamaPromisProject(models.Model):
    """
    Modèle principal pour les projets SAMA PROMIS.
    
    Hérite du modèle de base pour QR codes, workflows et audit.
    Implémente les cycles de vie spécifiques aux projets.
    """
    _name = 'sama.promis.project'
    _description = 'SAMA PROMIS Project'
    _inherit = ['sama.promis.base.model']
    _order = 'create_date desc, priority desc'

    # Redéfinition du champ state avec les états spécifiques aux projets
    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('submitted', 'Soumis'),
            ('under_review', 'En Révision'),
            ('approved', 'Approuvé'),
            ('in_progress', 'En Cours'),
            ('suspended', 'Suspendu'),
            ('completed', 'Terminé'),
            ('cancelled', 'Annulé')
        ],
        string='État',
        default='draft',
        tracking=True,
        help="État actuel du projet"
    )

    # Informations de base du projet
    project_type = fields.Selection(
        selection=[
            ('operational_call', 'Opérationnel (Appel à Propositions)'),
            ('operational_initiative', 'Opérationnel (Initiative du Programme)'),
            ('administrative', 'Administratif')
        ],
        string='Type de Projet',
        required=True,
        default='operational_call',
        tracking=True,
        help="Type de projet selon les spécifications SAMA PROMIS"
    )
    
    project_code = fields.Char(
        string='Code Projet',
        help="Code unique du projet"
    )
    
    short_description = fields.Text(
        string='Description Courte',
        help="Description courte pour affichage public"
    )
    
    objectives = fields.Text(
        string='Objectifs',
        help="Objectifs du projet"
    )
    
    expected_results = fields.Text(
        string='Résultats Attendus',
        help="Résultats attendus du projet"
    )
    
    # Partenaires et relations
    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire Principal',
        domain=[('is_beneficiary', '=', True)],
        help="Partenaire principal (bénéficiaire)"
    )
    
    donor_id = fields.Many2one(
        'res.partner',
        string='Bailleur de Fonds',
        domain=[('is_donor', '=', True)],
        required=True,
        tracking=True,
        help="Bailleur de fonds du projet"
    )
    
    implementing_partner_ids = fields.Many2many(
        'res.partner',
        'project_implementing_partner_rel',
        'project_id',
        'partner_id',
        string='Partenaires de Mise en Œuvre',
        domain=[('partner_type', 'in', ['implementing_partner', 'ngo', 'private_sector'])],
        help="Partenaires impliqués dans la mise en œuvre"
    )
    
    # Informations financières
    total_budget = fields.Monetary(
        string='Budget Total',
        currency_field='currency_id',
        tracking=True,
        help="Budget total du projet"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
        help="Devise du projet"
    )
    
    donor_contribution = fields.Monetary(
        string='Contribution Bailleur',
        currency_field='currency_id',
        help="Montant de la contribution du bailleur"
    )
    
    partner_contribution = fields.Monetary(
        string='Contribution Partenaire',
        currency_field='currency_id',
        help="Montant de la contribution du partenaire"
    )
    
    spent_amount = fields.Monetary(
        string='Montant Dépensé',
        currency_field='currency_id',
        compute='_compute_financial_data',
        store=True,
        help="Montant total dépensé"
    )
    
    remaining_budget = fields.Monetary(
        string='Budget Restant',
        currency_field='currency_id',
        compute='_compute_financial_data',
        store=True,
        help="Budget restant"
    )
    
    budget_utilization_rate = fields.Float(
        string='Taux d\'Utilisation Budget (%)',
        compute='_compute_financial_data',
        store=True,
        help="Pourcentage d'utilisation du budget"
    )
    
    # Dates et durée
    submission_date = fields.Date(
        string='Date de Soumission',
        help="Date de soumission du projet"
    )
    
    approval_date = fields.Date(
        string='Date d\'Approbation',
        help="Date d'approbation du projet"
    )
    
    actual_start_date = fields.Date(
        string='Date de Début Réelle',
        help="Date de début réelle du projet"
    )
    
    actual_end_date = fields.Date(
        string='Date de Fin Réelle',
        help="Date de fin réelle du projet"
    )
    
    # Localisation
    region = fields.Char(
        string='Région',
        help="Région d'intervention"
    )
    
    department = fields.Char(
        string='Département',
        help="Département d'intervention"
    )
    
    commune = fields.Char(
        string='Commune',
        help="Commune d'intervention"
    )
    
    target_population = fields.Integer(
        string='Population Cible',
        help="Nombre de bénéficiaires ciblés"
    )
    
    # Relations avec autres modèles
    call_for_proposal_id = fields.Many2one(
        'sama.promis.call.for.proposal',
        string='Appel à Propositions',
        help="Appel à propositions d'origine (si applicable)"
    )
    
    contract_ids = fields.One2many(
        'sama.promis.contract',
        'project_id',
        string='Contrats',
        help="Contrats associés au projet"
    )
    
    payment_ids = fields.One2many(
        'sama.promis.payment',
        'project_id',
        string='Paiements',
        help="Paiements du projet"
    )
    
    evaluation_ids = fields.One2many(
        'sama.promis.evaluation',
        'project_id',
        string='Évaluations',
        help="Évaluations du projet"
    )
    
    indicator_ids = fields.One2many(
        'sama.promis.performance.indicator',
        'project_id',
        string='Indicateurs de Performance',
        help="Indicateurs de performance du projet"
    )
    
    # Champs calculés
    progress_percentage = fields.Float(
        string='Pourcentage d\'Avancement',
        compute='_compute_progress',
        store=True,
        help="Pourcentage d'avancement du projet"
    )
    
    is_delayed = fields.Boolean(
        string='En Retard',
        compute='_compute_delays',
        help="Indique si le projet est en retard"
    )
    
    delay_days = fields.Integer(
        string='Jours de Retard',
        compute='_compute_delays',
        help="Nombre de jours de retard"
    )

    def _get_reference_prefix(self):
        """Retourne le préfixe de référence pour les projets."""
        type_prefixes = {
            'operational_call': 'PROJ-OC',
            'operational_initiative': 'PROJ-OI',
            'administrative': 'PROJ-ADM'
        }
        return type_prefixes.get(self.project_type, 'PROJ')

    @api.depends('payment_ids', 'total_budget', 'total_budget_computed', 'use_multi_source_funding')
    def _compute_financial_data(self):
        """Calcule les données financières."""
        for project in self:
            paid_payments = project.payment_ids.filtered(lambda p: p.state == 'paid')
            project.spent_amount = sum(paid_payments.mapped('amount'))
            
            # Use multi-source total if enabled, else use legacy total_budget
            effective_budget = project.total_budget_computed if project.use_multi_source_funding else project.total_budget
            project.remaining_budget = effective_budget - project.spent_amount
            
            if effective_budget > 0:
                project.budget_utilization_rate = (project.spent_amount / effective_budget) * 100
            else:
                project.budget_utilization_rate = 0

    @api.depends('indicator_ids', 'state')
    def _compute_progress(self):
        """Calcule le pourcentage d'avancement."""
        for project in self:
            if project.state == 'completed':
                project.progress_percentage = 100
            elif project.state in ['draft', 'submitted', 'under_review']:
                project.progress_percentage = 0
            elif project.state == 'approved':
                project.progress_percentage = 10
            elif project.state == 'in_progress':
                # Calcul basé sur les indicateurs si disponibles
                if project.indicator_ids:
                    total_indicators = len(project.indicator_ids)
                    completed_indicators = len(project.indicator_ids.filtered(lambda i: i.is_achieved))
                    project.progress_percentage = (completed_indicators / total_indicators) * 100
                else:
                    # Calcul basé sur les dates
                    if project.start_date and project.end_date:
                        today = fields.Date.today()
                        if today <= project.start_date:
                            project.progress_percentage = 10
                        elif today >= project.end_date:
                            project.progress_percentage = 90
                        else:
                            total_days = (project.end_date - project.start_date).days
                            elapsed_days = (today - project.start_date).days
                            project.progress_percentage = min(90, 10 + (elapsed_days / total_days) * 80)
                    else:
                        project.progress_percentage = 50  # Valeur par défaut
            else:
                project.progress_percentage = 0

    @api.depends('end_date', 'actual_end_date', 'state')
    def _compute_delays(self):
        """Calcule les retards."""
        today = fields.Date.today()
        for project in self:
            if project.state == 'completed' and project.actual_end_date and project.end_date:
                # Projet terminé : comparer date réelle vs prévue
                delay = (project.actual_end_date - project.end_date).days
                project.is_delayed = delay > 0
                project.delay_days = max(0, delay)
            elif project.state in ['in_progress', 'suspended'] and project.end_date:
                # Projet en cours : comparer avec aujourd'hui
                delay = (today - project.end_date).days
                project.is_delayed = delay > 0
                project.delay_days = max(0, delay)
            else:
                project.is_delayed = False
                project.delay_days = 0

    # Validation des transitions d'état (surcharge du mixin)
    def _validate_state_transition(self, new_state):
        """Valide les transitions d'état spécifiques aux projets."""
        current_state = self.state
        
        # Définition des transitions autorisées
        allowed_transitions = {
            'draft': ['submitted', 'cancelled'],
            'submitted': ['under_review', 'draft', 'cancelled'],
            'under_review': ['approved', 'submitted', 'cancelled'],
            'approved': ['in_progress', 'cancelled'],
            'in_progress': ['suspended', 'completed', 'cancelled'],
            'suspended': ['in_progress', 'cancelled'],
            'completed': [],  # État final
            'cancelled': ['draft']  # Possibilité de réactiver
        }
        
        return new_state in allowed_transitions.get(current_state, [])

    def _after_state_change(self, old_state, new_state):
        """Actions après changement d'état."""
        super()._after_state_change(old_state, new_state)
        
        # Actions spécifiques selon le nouvel état
        if new_state == 'submitted':
            self.submission_date = fields.Date.today()
        elif new_state == 'approved':
            self.approval_date = fields.Date.today()
        elif new_state == 'in_progress':
            if not self.actual_start_date:
                self.actual_start_date = fields.Date.today()
        elif new_state == 'completed':
            if not self.actual_end_date:
                self.actual_end_date = fields.Date.today()

    # Boutons d'action spécifiques aux projets
    def action_submit_for_review(self):
        """Soumet le projet pour révision."""
        if not self.partner_id:
            raise UserError(_("Un partenaire principal doit être défini avant la soumission."))
        
        # Use multi-source total if enabled, else use legacy total_budget
        effective_budget = self.total_budget_computed if self.use_multi_source_funding else self.total_budget
        if not effective_budget:
            raise UserError(_("Le budget total doit être défini avant la soumission."))
        
        self.change_state('submitted', 'Soumission pour révision')
        return True

    def action_start_review(self):
        """Démarre la révision du projet."""
        self.change_state('under_review', 'Début de la révision')
        return True

    def action_approve_project(self):
        """Approuve le projet."""
        if not self.donor_id:
            raise UserError(_("Un bailleur de fonds doit être défini avant l'approbation."))
        
        self.change_state('approved', 'Approbation du projet')
        return True

    def action_start_implementation(self):
        """Démarre la mise en œuvre du projet."""
        if not self.start_date:
            raise UserError(_("Une date de début doit être définie avant le démarrage."))
        
        self.change_state('in_progress', 'Début de la mise en œuvre')
        return True

    def action_suspend_project(self):
        """Suspend le projet."""
        return self.change_state('suspended', 'Suspension du projet')

    def action_resume_project(self):
        """Reprend le projet suspendu."""
        return self.change_state('in_progress', 'Reprise du projet')

    def action_complete_project(self):
        """Marque le projet comme terminé."""
        # Vérifications avant finalisation
        if self.budget_utilization_rate < 80:
            raise UserError(_("Le taux d'utilisation du budget est inférieur à 80%. Veuillez vérifier."))
        
        self.change_state('completed', 'Finalisation du projet')
        return True

    def action_cancel_project(self):
        """Annule le projet."""
        return self.change_state('cancelled', 'Annulation du projet')

    # Actions utilitaires
    def action_view_contracts(self):
        """Affiche les contrats du projet."""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Contrats - {self.name}',
            'res_model': 'sama.promis.contract',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_view_payments(self):
        """Affiche les paiements du projet."""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Paiements - {self.name}',
            'res_model': 'sama.promis.payment',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_view_evaluations(self):
        """Affiche les évaluations du projet."""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Évaluations - {self.name}',
            'res_model': 'sama.promis.evaluation',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    @api.model
    def get_dashboard_data(self):
        """Retourne les données pour le dashboard."""
        total_projects = self.search_count([])
        active_projects = self.search_count([('state', '=', 'in_progress')])
        completed_projects = self.search_count([('state', '=', 'completed')])
        delayed_projects = self.search_count([('is_delayed', '=', True)])
        
        # Statistiques par type
        type_stats = {}
        for ptype, label in self._fields['project_type'].selection:
            count = self.search_count([('project_type', '=', ptype)])
            type_stats[ptype] = {'label': label, 'count': count}
        
        # Budget total (considérer le mode multi-sources)
        all_projects = self.search([])
        total_budget = sum(
            project.total_budget_computed if project.use_multi_source_funding else project.total_budget
            for project in all_projects
        )
        spent_budget = sum(all_projects.mapped('spent_amount'))
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'delayed_projects': delayed_projects,
            'type_statistics': type_stats,
            'total_budget': total_budget,
            'spent_budget': spent_budget,
            'budget_utilization': (spent_budget / total_budget * 100) if total_budget > 0 else 0
        }