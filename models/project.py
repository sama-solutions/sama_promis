# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    # Project Type
    project_type = fields.Selection([
        ('operational_call', 'Projet Opérationnel (Appel à Propositions)'),
        ('operational_initiative', 'Projet Opérationnel (Initiative du Programme)'),
        ('administrative', 'Projet Administratif'),
    ], string="Type de Projet", required=True, tracking=True, default='operational_initiative')
    
    # Project Details
    donor_id = fields.Many2one('res.partner', string="Bailleur de Fonds", 
                             domain="[('is_company', '=', True), ('is_donor', '=', True)]",
                             tracking=True)
    call_for_proposal_id = fields.Many2one('sama.promis.call.proposal', 
                                         string="Appel à Propositions",
                                         tracking=True)
    start_date = fields.Date(string="Date de Début", tracking=True)
    end_date = fields.Date(string="Date de Fin Prévue", tracking=True)
    total_budget = fields.Monetary(string="Budget Total", 
                                 currency_field='currency_id',
                                 tracking=True)
    currency_id = fields.Many2one('res.currency', 
                                default=lambda self: self.env.company.currency_id)
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('under_review', 'En Cours d\'Évaluation'),
        ('approved', 'Approuvé'),
        ('in_progress', 'En Cours'),
        ('suspended', 'Suspendu'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], default='draft', tracking=True, group_expand='_expand_states')
    
    # Performance Indicators
    performance_indicator_ids = fields.One2many('sama.promis.performance.indicator', 
                                              'project_id', 
                                              string="Indicateurs de Performance")
    
    # Evaluation
    evaluation_ids = fields.One2many('sama.promis.project.evaluation', 'project_id',
                                   string="Évaluations")
    average_score = fields.Float(string="Note Moyenne", compute='_compute_evaluation_scores',
                               digits=(5, 2), store=True)
    evaluation_status = fields.Selection([
        ('not_started', 'Non commencé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
    ], string="Statut d'Évaluation", compute='_compute_evaluation_scores', store=True)
    
    # Document Management
    document_ids = fields.One2many('ir.attachment', 'res_id', 
                                 domain=[('res_model', '=', 'project.project')], 
                                 string="Documents")
    
    # Event Management (Phase 2)
    event_ids = fields.One2many('sama.promis.project.event', 'project_id',
                               string="Événements")
    event_count = fields.Integer(string="Nombre d'Événements", compute='_compute_event_count')
    
    # Donor Compliance Fields (Phase 2)
    donor_compliance_level = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
    ], string="Niveau de Conformité Bailleur", default='medium', tracking=True)
    
    reporting_frequency = fields.Selection([
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('semi_annual', 'Semestriel'),
        ('annual', 'Annuel'),
    ], string="Fréquence de Rapportage", default='quarterly', tracking=True)
    
    next_report_date = fields.Date(string="Prochaine Date de Rapport", tracking=True)
    
    # Constraints
    _sql_constraints = [
        ('check_dates', 'CHECK(start_date <= end_date)', 
         "La date de début doit être antérieure ou égale à la date de fin.")
    ]
    
    def _expand_states(self, states, domain, order):
        """Expand all states in group by"""
        return [state[0] for state in self._fields['state'].selection]
    
    @api.onchange('project_type')
    def _onchange_project_type(self):
        """Reset relevant fields when project type changes"""
        if self.project_type != 'operational_call':
            self.call_for_proposal_id = False
    
    @api.constrains('project_type', 'call_for_proposal_id')
    def _check_call_for_proposal(self):
        for project in self:
            if project.project_type == 'operational_call' and not project.call_for_proposal_id:
                raise ValidationError(_("Un appel à propositions est requis pour les projets opérationnels par appel."))

    @api.depends('event_ids')
    def _compute_event_count(self):
        """Compute the number of events for this project"""
        for project in self:
            project.event_count = len(project.event_ids)
    
    # Workflow Transition Methods
    def action_submit(self):
        """Submit project for review"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Seuls les projets en brouillon peuvent être soumis."))
        self.write({'state': 'submitted'})
        self._send_notification('submitted')
    
    def action_approve(self):
        """Approve project"""
        self.ensure_one()
        if self.state not in ['submitted', 'under_review']:
            raise UserError(_("Seuls les projets soumis ou en évaluation peuvent être approuvés."))

        self.write({'state': 'approved'})
        self._send_notification('approved')
    
    def action_start(self):
        """Start project execution"""
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Seuls les projets approuvés peuvent démarrer."))
        if not self.start_date:
            self.start_date = fields.Date.today()
        self.write({'state': 'in_progress'})
        self._send_notification('started')
    
    def action_complete(self):
        """Mark project as completed"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Seuls les projets en cours peuvent être marqués comme terminés."))

        self.write({
            'state': 'completed',
            'end_date': fields.Date.today()
        })
        self._send_notification('completed')
    
    def action_suspend(self):
        """Suspend project"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Seuls les projets en cours peuvent être suspendus."))
        self.write({'state': 'suspended'})
        self._send_notification('suspended')
    
    def action_resume(self):
        """Resume suspended project"""
        self.ensure_one()
        if self.state != 'suspended':
            raise UserError(_("Seuls les projets suspendus peuvent être repris."))
        self.write({'state': 'in_progress'})
        self._send_notification('resumed')
    
    def action_cancel(self):
        """Cancel project"""
        self.ensure_one()
        if self.state in ['completed', 'cancelled']:
            raise UserError(_("Les projets terminés ou annulés ne peuvent pas être annulés."))
        self.write({'state': 'cancelled'})
        self._send_notification('cancelled')
    
    @api.depends('evaluation_ids', 'evaluation_ids.state', 'evaluation_ids.score')
    def _compute_evaluation_scores(self):
        """Compute evaluation status and average score"""
        for project in self:
            evaluations = project.evaluation_ids.filtered(lambda e: e.state == 'completed')
            
            # Calculate average score
            if evaluations:
                project.average_score = sum(evaluations.mapped('score')) / len(evaluations)
            else:
                project.average_score = 0.0
            
            # Determine evaluation status
            if not project.evaluation_ids:
                project.evaluation_status = 'not_started'
            elif all(e.state == 'completed' for e in project.evaluation_ids):
                project.evaluation_status = 'completed'
            else:
                project.evaluation_status = 'in_progress'
    
    def _send_notification(self, notification_type):
        """Send notification based on project state change"""
        template = False
        template_xmlid = False
        
        # Map notification types to email templates
        template_mapping = {
            'submitted': 'sama_promis.email_template_project_submitted',
            'approved': 'sama_promis.email_template_project_approved',
            'started': 'sama_promis.email_template_project_started',
            'completed': 'sama_promis.email_template_project_completed',
            'suspended': 'sama_promis.email_template_project_suspended',
            'resumed': 'sama_promis.email_template_project_resumed',
            'cancelled': 'sama_promis.email_template_project_cancelled',
        }
        
        template_xmlid = template_mapping.get(notification_type)
        if template_xmlid:
            template = self.env.ref(template_xmlid, raise_if_not_found=False)
            
        if template:
            template.send_mail(self.id, force_send=True)


class SamaPromisProjectEvent(models.Model):
    _name = 'sama.promis.project.event'
    _description = 'Événement de Projet SAMA PROMIS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string="Nom de l'Événement", required=True, tracking=True)
    project_id = fields.Many2one('project.project', string="Projet", 
                                required=True, ondelete='cascade', tracking=True)
    
    # Event Details
    event_type = fields.Selection([
        ('conference', 'Conférence'),
        ('workshop', 'Atelier'),
        ('meeting', 'Réunion'),
        ('training', 'Formation'),
        ('ceremony', 'Cérémonie'),
        ('other', 'Autre'),
    ], string="Type d'Événement", required=True, tracking=True)
    
    start_date = fields.Datetime(string="Date et Heure de Début", required=True, tracking=True)
    end_date = fields.Datetime(string="Date et Heure de Fin", required=True, tracking=True)
    
    # Location
    location = fields.Char(string="Lieu", tracking=True)
    address = fields.Text(string="Adresse Complète")
    
    # Description
    description = fields.Html(string="Description")
    objectives = fields.Text(string="Objectifs")
    
    # Participants
    expected_participants = fields.Integer(string="Nombre de Participants Attendus", tracking=True)
    actual_participants = fields.Integer(string="Nombre de Participants Réels", tracking=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En Cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string="Statut", default='draft', tracking=True)
    
    # Budget
    budget = fields.Monetary(string="Budget", currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(related='project_id.currency_id', string="Devise", store=True)
    actual_cost = fields.Monetary(string="Coût Réel", currency_field='currency_id', tracking=True)
    
    # Documents
    document_ids = fields.One2many('ir.attachment', 'res_id',
                                 domain=[('res_model', '=', 'sama.promis.project.event')],
                                 string="Documents")
    
    # Reporting
    report_ids = fields.One2many('sama.promis.event.report', 'event_id', string="Rapports")
    
    _sql_constraints = [
        ('check_dates', 'CHECK(start_date <= end_date)',
         "La date de début doit être antérieure ou égale à la date de fin.")
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code('sama.promis.project.event') or _('New')
        return super().create(vals_list)
    
    def action_confirm(self):
        """Confirm event"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Seuls les événements en brouillon peuvent être confirmés."))
        self.write({'state': 'confirmed'})
        self._send_notification('confirmed')
    
    def action_start(self):
        """Start event"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("Seuls les événements confirmés peuvent démarrer."))
        self.write({'state': 'in_progress'})
        self._send_notification('started')
    
    def action_complete(self):
        """Complete event"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Seuls les événements en cours peuvent être terminés."))
        self.write({'state': 'completed'})
        self._send_notification('completed')
    
    def action_cancel(self):
        """Cancel event"""
        self.ensure_one()
        if self.state in ['completed', 'cancelled']:
            raise UserError(_("Les événements terminés ou annulés ne peuvent pas être annulés."))
        self.write({'state': 'cancelled'})
        self._send_notification('cancelled')
    
    def _send_notification(self, notification_type):
        """Send notification based on event state change"""
        self.message_post(
            body=_("Event %s has been %s.") % (self.name, notification_type),
            subject=_("Event Status Update"),
            message_type='notification'
        )


class SamaPromisEventReport(models.Model):
    _name = 'sama.promis.event.report'
    _description = 'Rapport d\'Événement SAMA PROMIS'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string="Titre du Rapport", required=True, tracking=True)
    event_id = fields.Many2one('sama.promis.project.event', string="Événement", 
                              required=True, ondelete='cascade')
    
    # Report Details
    report_date = fields.Date(string="Date du Rapport", default=fields.Date.today, tracking=True)
    author_id = fields.Many2one('res.users', string="Auteur", default=lambda self: self.env.user, tracking=True)
    
    # Content
    summary = fields.Text(string="Résumé", required=True)
    key_achievements = fields.Text(string="Réalisations Clés")
    challenges = fields.Text(string="Défis Rencontrés")
    recommendations = fields.Text(string="Recommandations")
    
    # Metrics
    attendance_rate = fields.Float(string="Taux de Participation (%)", digits=(5, 2))
    satisfaction_score = fields.Float(string="Score de Satisfaction", digits=(3, 1))
    
    # Status
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ], string="Statut", default='draft', tracking=True)
    
    # Documents
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                   domain=[('res_model', '=', 'sama.promis.event.report')],
                                   string="Pièces Jointes")
    
    def action_submit(self):
        """Submit report"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Seuls les rapports en brouillon peuvent être soumis."))
        self.write({'state': 'submitted'})
    
    def action_approve(self):
        """Approve report"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_("Seuls les rapports soumis peuvent être approuvés."))
        self.write({'state': 'approved'})
    
    def action_reject(self):
        """Reject report"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_("Seuls les rapports soumis peuvent être rejetés."))
        self.write({'state': 'rejected'})
