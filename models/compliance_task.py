# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class SamaPromisComplianceTask(models.Model):
    """Tâche de Conformité - Individual compliance items (milestones, checklists, deliverables)."""
    
    _name = 'sama.promis.compliance.task'
    _description = 'Tâche de Conformité'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sama.promis.workflow.mixin']
    _order = 'deadline, sequence, id'
    _rec_name = 'name'
    
    # Core Fields
    name = fields.Char(
        string='Nom de la Tâche',
        required=True,
        tracking=True,
        help="Nom/titre de la tâche de conformité"
    )
    description = fields.Html(
        string='Description',
        help="Description détaillée de la tâche"
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help="Ordre d'affichage"
    )
    task_type = fields.Selection([
        ('milestone', 'Jalon'),
        ('deliverable', 'Livrable'),
        ('report', 'Rapport'),
        ('review', 'Revue'),
        ('approval', 'Approbation'),
        ('checklist', 'Checklist'),
        ('other', 'Autre')
    ], string='Type de Tâche', required=True, default='other',
        help="Type de tâche de conformité")
    
    compliance_profile_id = fields.Many2one(
        'sama.promis.compliance.profile',
        string='Profil de Conformité',
        help="Profil de conformité source (optionnel)"
    )
    
    # Relationships
    project_id = fields.Many2one(
        'sama.promis.project',
        string='Projet',
        ondelete='cascade',
        help="Projet parent"
    )
    contract_id = fields.Many2one(
        'sama.promis.contract',
        string='Contrat',
        ondelete='cascade',
        help="Contrat parent (optionnel)"
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True,
        required=True,
        help="Personne responsable de cette tâche"
    )
    
    # State Management (override from WorkflowMixin)
    state = fields.Selection([
        ('pending', 'En Attente'),
        ('in_progress', 'En Cours'),
        ('submitted', 'Soumis'),
        ('under_review', 'En Révision'),
        ('approved', 'Approuvé'),
        ('completed', 'Terminé'),
        ('overdue', 'En Retard'),
        ('cancelled', 'Annulé')
    ], string='État', default='pending', required=True, tracking=True,
        help="État actuel de la tâche")
    
    # Timeline
    deadline = fields.Date(
        string='Échéance',
        required=True,
        tracking=True,
        help="Date limite pour cette tâche"
    )
    planned_completion_date = fields.Date(
        string='Date de Complétion Prévue',
        help="Date prévue de complétion"
    )
    actual_completion_date = fields.Date(
        string='Date de Complétion Réelle',
        readonly=True,
        help="Date réelle de complétion"
    )
    days_until_deadline = fields.Integer(
        string='Jours Restants',
        compute='_compute_days_until_deadline',
        store=True,
        help="Nombre de jours jusqu'à l'échéance"
    )
    is_overdue = fields.Boolean(
        string='En Retard',
        compute='_compute_overdue_status',
        store=True,
        help="Indique si la tâche est en retard"
    )
    days_overdue = fields.Integer(
        string='Jours de Retard',
        compute='_compute_overdue_status',
        store=True,
        help="Nombre de jours de retard"
    )
    
    # Compliance Details
    priority = fields.Selection([
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevée'),
        ('critical', 'Critique')
    ], string='Priorité', default='normal',
        help="Niveau de priorité de la tâche")
    
    requires_document = fields.Boolean(
        string='Requiert Document',
        default=False,
        help="Indique si un document doit être joint"
    )
    document_ids = fields.Many2many(
        'ir.attachment',
        'compliance_task_attachment_rel',
        'task_id',
        'attachment_id',
        string='Documents',
        help="Documents joints à cette tâche"
    )
    requires_approval = fields.Boolean(
        string='Requiert Approbation',
        default=False,
        help="Indique si une approbation est nécessaire"
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approuvé Par',
        readonly=True,
        help="Utilisateur qui a approuvé"
    )
    approval_date = fields.Date(
        string='Date d\'Approbation',
        readonly=True,
        help="Date d'approbation"
    )
    approval_notes = fields.Text(
        string='Notes d\'Approbation',
        help="Notes/commentaires d'approbation"
    )
    
    # Checklist Items (for task_type='checklist')
    checklist_items = fields.Text(
        string='Éléments de Checklist',
        help="Éléments de checklist au format JSON avec statut de complétion"
    )
    checklist_completion_rate = fields.Float(
        string='Taux de Complétion Checklist',
        compute='_compute_checklist_completion',
        store=True,
        help="Pourcentage d'éléments de checklist complétés"
    )
    
    # Notifications
    reminder_sent = fields.Boolean(
        string='Rappel Envoyé',
        default=False,
        help="Indique si un rappel a été envoyé"
    )
    reminder_sent_date = fields.Date(
        string='Date Rappel',
        help="Date d'envoi du rappel"
    )
    escalation_sent = fields.Boolean(
        string='Escalade Envoyée',
        default=False,
        help="Indique si une escalade a été envoyée"
    )
    escalation_sent_date = fields.Date(
        string='Date Escalade',
        help="Date d'envoi de l'escalade"
    )
    
    _sql_constraints = [
        ('check_completion_date',
         'CHECK(actual_completion_date IS NULL OR actual_completion_date <= CURRENT_DATE)',
         'La date de complétion réelle ne peut pas être dans le futur!')
    ]
    
    @api.constrains('project_id', 'contract_id')
    def _check_project_or_contract(self):
        """Must have either project_id or contract_id (at least one)."""
        for task in self:
            if not task.project_id and not task.contract_id:
                raise ValidationError(_('Une tâche de conformité doit être liée à un projet ou un contrat.'))
    
    @api.depends('deadline')
    def _compute_days_until_deadline(self):
        """Calculate days remaining until deadline."""
        today = date.today()
        for task in self:
            if task.deadline:
                delta = task.deadline - today
                task.days_until_deadline = delta.days
            else:
                task.days_until_deadline = 0
    
    @api.depends('deadline', 'state')
    def _compute_overdue_status(self):
        """Calculate if task is overdue and days overdue."""
        today = date.today()
        completed_states = ['completed', 'cancelled', 'approved']
        
        for task in self:
            if task.deadline and task.state not in completed_states:
                if task.deadline < today:
                    task.is_overdue = True
                    delta = today - task.deadline
                    task.days_overdue = delta.days
                else:
                    task.is_overdue = False
                    task.days_overdue = 0
            else:
                task.is_overdue = False
                task.days_overdue = 0
    
    @api.depends('checklist_items')
    def _compute_checklist_completion(self):
        """Parse JSON and calculate completion percentage."""
        import json
        
        for task in self:
            if not task.checklist_items or task.task_type != 'checklist':
                task.checklist_completion_rate = 0.0
                continue
            
            try:
                items = json.loads(task.checklist_items)
                if not items:
                    task.checklist_completion_rate = 0.0
                    continue
                
                completed = sum(1 for item in items if item.get('completed', False))
                total = len(items)
                task.checklist_completion_rate = (completed / total * 100) if total > 0 else 0.0
            except (json.JSONDecodeError, ValueError, TypeError):
                task.checklist_completion_rate = 0.0
    
    def _validate_state_transition(self, new_state):
        """Define allowed state transitions."""
        self.ensure_one()
        
        allowed_transitions = {
            'pending': ['in_progress', 'cancelled'],
            'in_progress': ['submitted', 'completed', 'cancelled'],
            'submitted': ['under_review', 'in_progress', 'cancelled'],
            'under_review': ['approved', 'completed', 'in_progress', 'cancelled'],
            'approved': ['completed'],
            'completed': [],
            'overdue': ['in_progress', 'submitted', 'completed', 'cancelled'],
            'cancelled': []
        }
        
        current_state = self.state
        if new_state not in allowed_transitions.get(current_state, []):
            raise ValidationError(_(
                'Transition invalide de "%s" vers "%s".'
            ) % (dict(self._fields['state'].selection).get(current_state),
                 dict(self._fields['state'].selection).get(new_state)))
        
        return True
    
    def _before_state_change(self, new_state):
        """Validate requirements before state change."""
        self.ensure_one()
        
        # If submitting and requires_document, must have documents
        if new_state == 'submitted' and self.requires_document:
            if not self.document_ids:
                raise ValidationError(_('Cette tâche requiert au moins un document avant soumission.'))
        
        return super()._before_state_change(new_state)
    
    def _after_state_change(self, old_state, new_state):
        """Actions after state change."""
        self.ensure_one()
        
        # Set completion date when moving to completed or approved
        if new_state in ['completed', 'approved'] and not self.actual_completion_date:
            self.actual_completion_date = date.today()
        
        # Set approved_by when approving
        if new_state == 'approved' and not self.approved_by:
            self.approved_by = self.env.user
            self.approval_date = date.today()
        
        # Send notifications
        if new_state == 'submitted' and self.requires_approval:
            self._create_approval_activity()
        
        return super()._after_state_change(old_state, new_state)
    
    def action_mark_completed(self):
        """Mark task as completed."""
        for task in self:
            task.write({
                'state': 'completed',
                'actual_completion_date': date.today()
            })
        return True
    
    def action_request_approval(self):
        """Change state to submitted and create activity for approver."""
        for task in self:
            task.action_submit()
        return True
    
    def action_approve(self):
        """Approve task."""
        for task in self:
            task.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approval_date': date.today()
            })
        return True
    
    def action_reject(self):
        """Reject task, send back to in_progress."""
        for task in self:
            task.write({'state': 'in_progress'})
            # Post message
            task.message_post(
                body=_('Tâche rejetée par %s') % self.env.user.name,
                message_type='notification'
            )
        return True
    
    def update_checklist_item(self, item_index, completed):
        """Update specific checklist item completion status.
        
        Args:
            item_index: Index of the item to update
            completed: Boolean completion status
        """
        self.ensure_one()
        import json
        
        if not self.checklist_items:
            return False
        
        try:
            items = json.loads(self.checklist_items)
            if 0 <= item_index < len(items):
                items[item_index]['completed'] = completed
                self.checklist_items = json.dumps(items)
                return True
        except (json.JSONDecodeError, ValueError, IndexError):
            pass
        
        return False
    
    def send_reminder_notification(self):
        """Send reminder email to responsible user."""
        self.ensure_one()
        
        template = self.env.ref('sama_promis.mail_template_compliance_task_reminder', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        self.write({
            'reminder_sent': True,
            'reminder_sent_date': date.today()
        })
        
        return True
    
    def send_escalation_notification(self):
        """Send escalation email to project manager and compliance officers."""
        self.ensure_one()
        
        template = self.env.ref('sama_promis.mail_template_compliance_task_escalation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        self.write({
            'escalation_sent': True,
            'escalation_sent_date': date.today()
        })
        
        return True
    
    def _create_approval_activity(self):
        """Create activity for approver when task is submitted."""
        self.ensure_one()
        
        # Determine who should approve
        approver = self.project_id.created_by if self.project_id else self.env.user
        
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=approver.id,
            summary=_('Approbation requise: %s') % self.name,
            note=_('Veuillez approuver ou rejeter cette tâche de conformité.')
        )
    
    @api.model
    def cron_send_compliance_reminders(self):
        """Cron job to send reminders for upcoming deadlines."""
        today = date.today()
        
        # Find tasks that need reminders
        tasks = self.search([
            ('state', 'not in', ['completed', 'cancelled', 'approved']),
            ('reminder_sent', '=', False),
            ('deadline', '!=', False)
        ])
        
        for task in tasks:
            if task.compliance_profile_id:
                reminder_days = task.compliance_profile_id.reminder_days_before
            else:
                reminder_days = 7  # Default
            
            days_until = (task.deadline - today).days
            if 0 <= days_until <= reminder_days:
                task.send_reminder_notification()
        
        return True
    
    @api.model
    def cron_send_compliance_escalations(self):
        """Cron job to send escalations for overdue tasks."""
        today = date.today()
        
        # Find overdue tasks that need escalation
        tasks = self.search([
            ('is_overdue', '=', True),
            ('escalation_sent', '=', False),
            ('state', 'not in', ['completed', 'cancelled', 'approved'])
        ])
        
        for task in tasks:
            if task.compliance_profile_id:
                escalation_days = task.compliance_profile_id.escalation_days_after
            else:
                escalation_days = 3  # Default
            
            if task.days_overdue >= escalation_days:
                task.send_escalation_notification()
        
        return True
