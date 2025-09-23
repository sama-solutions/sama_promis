# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Modèle Projet
===========================

Modèle principal pour la gestion des projets avec cycles de vie complets.
"""

from odoo import models, fields, api
from datetime import datetime, timedelta
import uuid
import base64
import io


class SamaPromisProject(models.Model):
    """Modèle principal pour les projets SAMA PROMIS."""
    
    _name = 'sama.promis.project'
    _description = 'Projet SAMA PROMIS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    # Champs de base
    name = fields.Char(
        string='Nom du Projet',
        required=True,
        tracking=True,
        help="Nom complet du projet"
    )
    
    reference = fields.Char(
        string='Référence',
        readonly=True,
        copy=False,
        help="Référence unique générée automatiquement"
    )
    
    description = fields.Html(
        string='Description',
        help="Description détaillée du projet"
    )
    
    objectives = fields.Html(
        string='Objectifs',
        help="Objectifs du projet"
    )
    
    expected_results = fields.Html(
        string='Résultats Attendus',
        help="Résultats attendus du projet"
    )

    # Type et priorité
    project_type = fields.Selection([
        ('development', 'Développement'),
        ('infrastructure', 'Infrastructure'),
        ('education', 'Éducation'),
        ('health', 'Santé'),
        ('agriculture', 'Agriculture'),
        ('environment', 'Environnement'),
        ('social', 'Social'),
        ('economic', 'Économique'),
    ], string='Type de Projet', required=True, default='development', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ], string='Priorité', default='normal', tracking=True)

    # État et workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('under_review', 'En Révision'),
        ('approved', 'Approuvé'),
        ('in_progress', 'En Cours'),
        ('suspended', 'Suspendu'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True, required=True)

    # Partenaires
    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire Principal',
        required=True,
        help="Partenaire principal du projet"
    )
    
    donor_id = fields.Many2one(
        'res.partner',
        string='Bailleur de Fonds',
        domain=[('is_donor', '=', True)],
        help="Bailleur de fonds du projet"
    )
    
    implementing_partner_ids = fields.Many2many(
        'res.partner',
        'project_implementing_partner_rel',
        'project_id',
        'partner_id',
        string='Partenaires de Mise en Œuvre',
        domain=[('is_implementing_partner', '=', True)]
    )

    # Dates
    start_date = fields.Date(
        string='Date de Début',
        tracking=True
    )
    
    end_date = fields.Date(
        string='Date de Fin',
        tracking=True
    )
    
    submission_date = fields.Date(
        string='Date de Soumission',
        readonly=True
    )
    
    approval_date = fields.Date(
        string='Date d\'Approbation',
        readonly=True
    )
    
    actual_start_date = fields.Date(
        string='Date de Début Réelle',
        readonly=True
    )
    
    actual_end_date = fields.Date(
        string='Date de Fin Réelle',
        readonly=True
    )
    
    deadline = fields.Date(
        string='Date Limite',
        tracking=True
    )

    # Budget et finances
    total_budget = fields.Monetary(
        string='Budget Total',
        currency_field='currency_id',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )
    
    donor_contribution = fields.Monetary(
        string='Contribution Bailleur',
        currency_field='currency_id'
    )
    
    partner_contribution = fields.Monetary(
        string='Contribution Partenaire',
        currency_field='currency_id'
    )
    
    spent_amount = fields.Monetary(
        string='Montant Dépensé',
        currency_field='currency_id',
        readonly=True
    )

    # Localisation
    region = fields.Char(string='Région')
    department = fields.Char(string='Département')
    commune = fields.Char(string='Commune')
    target_population = fields.Integer(string='Population Cible')

    # QR Code
    qr_code_data = fields.Char(
        string='Données QR Code',
        compute='_compute_qr_code_data',
        store=True
    )
    
    qr_code_image = fields.Binary(
        string='Image QR Code',
        compute='_compute_qr_code_image',
        store=True
    )
    
    qr_code_url = fields.Char(
        string='URL QR Code',
        compute='_compute_qr_code_url',
        store=True
    )

    # Champs calculés
    duration_days = fields.Integer(
        string='Durée (jours)',
        compute='_compute_duration',
        store=True
    )
    
    progress_percentage = fields.Float(
        string='Progression (%)',
        compute='_compute_progress',
        store=True
    )
    
    remaining_budget = fields.Monetary(
        string='Budget Restant',
        compute='_compute_remaining_budget',
        currency_field='currency_id'
    )
    
    budget_utilization_rate = fields.Float(
        string='Taux d\'Utilisation Budget (%)',
        compute='_compute_budget_utilization'
    )
    
    is_delayed = fields.Boolean(
        string='En Retard',
        compute='_compute_delays'
    )
    
    delay_days = fields.Integer(
        string='Jours de Retard',
        compute='_compute_delays'
    )
    
    days_to_deadline = fields.Integer(
        string='Jours jusqu\'à l\'Échéance',
        compute='_compute_days_to_deadline'
    )

    # Audit et traçabilité
    created_by = fields.Many2one(
        'res.users',
        string='Créé par',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    created_date = fields.Datetime(
        string='Date de Création',
        default=fields.Datetime.now,
        readonly=True
    )
    
    last_modified_by = fields.Many2one(
        'res.users',
        string='Modifié par',
        readonly=True
    )
    
    last_modified_date = fields.Datetime(
        string='Date de Modification',
        readonly=True
    )
    
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True
    )
    
    state_history = fields.Text(
        string='Historique des États',
        readonly=True
    )

    # Tags
    tag_ids = fields.Many2many(
        'sama.promis.tag',
        string='Étiquettes'
    )

    @api.model
    def create(self, vals):
        """Surcharge de create pour générer la référence."""
        if not vals.get('reference'):
            vals['reference'] = self._generate_reference()
        
        # Initialiser l'historique des états
        if 'state' in vals:
            vals['state_history'] = f"Création: {vals['state']} le {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return super().create(vals)

    def write(self, vals):
        """Surcharge de write pour l'audit."""
        # Mise à jour des champs d'audit
        vals['last_modified_by'] = self.env.user.id
        vals['last_modified_date'] = fields.Datetime.now()
        vals['version'] = self.version + 1
        
        # Historique des changements d'état
        if 'state' in vals:
            old_state = self.state
            new_state = vals['state']
            if old_state != new_state:
                history_line = f"\n{old_state} → {new_state} le {datetime.now().strftime('%d/%m/%Y %H:%M')} par {self.env.user.name}"
                vals['state_history'] = (self.state_history or '') + history_line
        
        return super().write(vals)

    def _generate_reference(self):
        """Génère une référence unique."""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_part = str(uuid.uuid4().int)[:6]
        return f"SP-{timestamp}-{random_part}"

    @api.depends('name', 'reference')
    def _compute_qr_code_data(self):
        """Calcule les données du QR code."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://sama-promis.sn')
        for record in self:
            if record.id:
                record.qr_code_data = f"{base_url}/promispublic/project/{record.id}"
            else:
                record.qr_code_data = False

    @api.depends('qr_code_data')
    def _compute_qr_code_image(self):
        """Génère l'image du QR code."""
        try:
            import qrcode
            
            for record in self:
                if record.qr_code_data:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(record.qr_code_data)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    
                    record.qr_code_image = base64.b64encode(buffer.getvalue()).decode()
                else:
                    record.qr_code_image = False
        except ImportError:
            for record in self:
                record.qr_code_image = False

    @api.depends('qr_code_data')
    def _compute_qr_code_url(self):
        """Calcule l'URL du QR code."""
        for record in self:
            record.qr_code_url = record.qr_code_data or False

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calcule la durée en jours."""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_days = abs(delta.days)
            else:
                record.duration_days = 0

    @api.depends('state', 'start_date', 'end_date')
    def _compute_progress(self):
        """Calcule le pourcentage de progression."""
        for record in self:
            if record.state == 'draft':
                record.progress_percentage = 0
            elif record.state == 'submitted':
                record.progress_percentage = 10
            elif record.state == 'under_review':
                record.progress_percentage = 20
            elif record.state == 'approved':
                record.progress_percentage = 30
            elif record.state == 'in_progress':
                if record.start_date and record.end_date:
                    today = fields.Date.today()
                    if today <= record.start_date:
                        record.progress_percentage = 30
                    elif today >= record.end_date:
                        record.progress_percentage = 90
                    else:
                        total_days = (record.end_date - record.start_date).days
                        elapsed_days = (today - record.start_date).days
                        progress = 30 + (60 * elapsed_days / total_days)
                        record.progress_percentage = min(progress, 90)
                else:
                    record.progress_percentage = 50
            elif record.state == 'suspended':
                record.progress_percentage = record.progress_percentage or 50
            elif record.state == 'completed':
                record.progress_percentage = 100
            elif record.state == 'cancelled':
                record.progress_percentage = 0

    @api.depends('total_budget', 'spent_amount')
    def _compute_remaining_budget(self):
        """Calcule le budget restant."""
        for record in self:
            record.remaining_budget = record.total_budget - record.spent_amount

    @api.depends('total_budget', 'spent_amount')
    def _compute_budget_utilization(self):
        """Calcule le taux d'utilisation du budget."""
        for record in self:
            if record.total_budget > 0:
                record.budget_utilization_rate = (record.spent_amount / record.total_budget) * 100
            else:
                record.budget_utilization_rate = 0

    @api.depends('end_date', 'deadline')
    def _compute_delays(self):
        """Calcule les retards."""
        today = fields.Date.today()
        for record in self:
            if record.end_date and today > record.end_date and record.state != 'completed':
                record.is_delayed = True
                record.delay_days = (today - record.end_date).days
            elif record.deadline and today > record.deadline and record.state != 'completed':
                record.is_delayed = True
                record.delay_days = (today - record.deadline).days
            else:
                record.is_delayed = False
                record.delay_days = 0

    @api.depends('deadline')
    def _compute_days_to_deadline(self):
        """Calcule les jours jusqu'à l'échéance."""
        today = fields.Date.today()
        for record in self:
            if record.deadline:
                delta = record.deadline - today
                record.days_to_deadline = delta.days
            else:
                record.days_to_deadline = 0

    # Actions de workflow
    def action_submit_for_review(self):
        """Soumettre le projet pour révision."""
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.today()
        })
        return True

    def action_start_review(self):
        """Commencer la révision."""
        self.write({'state': 'under_review'})
        return True

    def action_approve_project(self):
        """Approuver le projet."""
        self.write({
            'state': 'approved',
            'approval_date': fields.Date.today()
        })
        return True

    def action_start_implementation(self):
        """Démarrer la mise en œuvre."""
        self.write({
            'state': 'in_progress',
            'actual_start_date': fields.Date.today()
        })
        return True

    def action_suspend_project(self):
        """Suspendre le projet."""
        self.write({'state': 'suspended'})
        return True

    def action_resume_project(self):
        """Reprendre le projet."""
        self.write({'state': 'in_progress'})
        return True

    def action_complete_project(self):
        """Terminer le projet."""
        self.write({
            'state': 'completed',
            'actual_end_date': fields.Date.today()
        })
        return True

    def action_cancel_project(self):
        """Annuler le projet."""
        self.write({'state': 'cancelled'})
        return True

    def action_view_qr_code(self):
        """Afficher le QR code."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'QR Code',
            'res_model': 'sama.promis.project',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sama_promis.view_sama_promis_project_qr_popup').id,
            'target': 'new',
        }