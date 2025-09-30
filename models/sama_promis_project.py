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
        currency_field='currency_id',
        help="DEPRECATED: Utiliser le mode multi-sources pour plus de flexibilité"
    )
    
    partner_contribution = fields.Monetary(
        string='Contribution Partenaire',
        currency_field='currency_id',
        help="DEPRECATED: Utiliser le mode multi-sources pour plus de flexibilité"
    )
    
    spent_amount = fields.Monetary(
        string='Montant Dépensé',
        currency_field='currency_id',
        readonly=True
    )
    
    # Multi-source funding fields
    use_multi_source_funding = fields.Boolean(
        string='Utiliser le Financement Multi-Sources',
        default=False,
        tracking=True,
        help="Activer pour gérer plusieurs sources de financement"
    )
    
    funding_source_ids = fields.One2many(
        'sama.promis.project.funding.source',
        'project_id',
        string='Sources de Financement',
        help="Liste de toutes les sources de financement pour ce projet"
    )
    
    total_budget_computed = fields.Monetary(
        string='Budget Total Calculé',
        compute='_compute_funding_totals',
        store=True,
        currency_field='currency_id',
        help="Somme de toutes les sources de financement (en mode multi-sources)"
    )
    
    total_international_funding = fields.Monetary(
        string='Financement International Total',
        compute='_compute_funding_totals',
        store=True,
        currency_field='currency_id',
        help="Somme des financements internationaux"
    )
    
    total_local_funding = fields.Monetary(
        string='Financement Local Total',
        compute='_compute_funding_totals',
        store=True,
        currency_field='currency_id',
        help="Somme des financements locaux"
    )
    
    funding_sources_count = fields.Integer(
        string='Nombre de Sources',
        compute='_compute_funding_totals',
        store=True,
        help="Nombre de sources de financement"
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

    call_for_proposal_id = fields.Many2one(
        'sama.promis.call.proposal',
        string='Appel à Propositions'
    )

    contract_ids = fields.One2many(
        'sama.promis.contract',
        'project_id',
        string='Contrats'
    )

    payment_ids = fields.One2many(
        'sama.promis.payment.request',
        'project_id',
        string='Paiements'
    )

    evaluation_ids = fields.One2many(
        'sama.promis.project.evaluation',
        'project_id',
        string='Évaluations'
    )

    procurement_plan_ids = fields.One2many(
        'sama.promis.procurement.plan',
        'project_id',
        string='Plans de Passation de Marché',
        help="Plans de passation de marché liés à ce projet"
    )

    procurement_plan_count = fields.Integer(
        string='Nombre de Plans de Passation',
        compute='_compute_procurement_plan_count',
        store=False
    )
    
    # Compliance Profile
    compliance_profile_id = fields.Many2one(
        'sama.promis.compliance.profile',
        string='Profil de Conformité',
        compute='_compute_compliance_profile',
        store=True,
        tracking=True,
        help="Profil de conformité à utiliser (calculé depuis le bailleur ou défini manuellement)"
    )
    compliance_profile_manual = fields.Many2one(
        'sama.promis.compliance.profile',
        string='Profil de Conformité Manuel',
        help="Remplacement manuel du profil de conformité"
    )
    use_compliance_profile = fields.Boolean(
        string='Utiliser Conformité',
        default=True,
        tracking=True,
        help="Activer la gestion de conformité"
    )
    
    # Compliance Tasks
    compliance_task_ids = fields.One2many(
        'sama.promis.compliance.task',
        'project_id',
        string='Tâches de Conformité',
        help="Liste des tâches de conformité"
    )
    compliance_task_count = fields.Integer(
        string='Nombre de Tâches',
        compute='_compute_compliance_statistics',
        store=True,
        help="Nombre de tâches de conformité"
    )
    compliance_tasks_completed = fields.Integer(
        string='Tâches Complétées',
        compute='_compute_compliance_statistics',
        store=True,
        help="Nombre de tâches complétées"
    )
    compliance_rate = fields.Float(
        string='Taux de Conformité',
        compute='_compute_compliance_statistics',
        store=True,
        help="Pourcentage de tâches complétées"
    )
    overdue_compliance_tasks = fields.Integer(
        string='Tâches en Retard',
        compute='_compute_compliance_statistics',
        store=True,
        help="Nombre de tâches en retard"
    )
    
    # Reporting Compliance
    last_compliance_report_date = fields.Date(
        string='Dernier Rapport',
        readonly=True,
        help="Date du dernier rapport de conformité"
    )
    next_compliance_report_date = fields.Date(
        string='Prochain Rapport',
        compute='_compute_next_compliance_report_date',
        store=True,
        help="Date du prochain rapport dû"
    )
    compliance_report_status = fields.Selection([
        ('on_time', 'À Jour'),
        ('due_soon', 'Échéance Proche'),
        ('overdue', 'En Retard')
    ], string='Statut Rapport',
        compute='_compute_compliance_report_status',
        help="Statut du rapport de conformité")

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
        # TODO: Pointer vers le portail public une fois développé
        # Pour l'instant, on pointe vers le backend Odoo
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://sama-promis.sn')
        for record in self:
            if record.id:
                # Format backend: /web#id={id}&model={model}&view_type=form
                record.qr_code_data = f"{base_url}/web#id={record.id}&model=sama.promis.project&view_type=form"
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

    @api.depends('total_budget', 'total_budget_computed', 'spent_amount', 'use_multi_source_funding')
    def _compute_remaining_budget(self):
        """Calcule le budget restant."""
        for record in self:
            effective_budget = record.total_budget_computed if record.use_multi_source_funding else record.total_budget
            record.remaining_budget = effective_budget - record.spent_amount

    @api.depends('total_budget', 'total_budget_computed', 'spent_amount', 'use_multi_source_funding')
    def _compute_budget_utilization(self):
        """Calcule le taux d'utilisation du budget."""
        for record in self:
            effective_budget = record.total_budget_computed if record.use_multi_source_funding else record.total_budget
            if effective_budget > 0:
                record.budget_utilization_rate = (record.spent_amount / effective_budget) * 100
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
    
    @api.depends('funding_source_ids', 'funding_source_ids.amount', 
                 'funding_source_ids.currency_id', 'funding_source_ids.funding_origin',
                 'use_multi_source_funding')
    def _compute_funding_totals(self):
        """Calcule les totaux de financement à partir des sources."""
        for project in self:
            if project.use_multi_source_funding and project.funding_source_ids:
                total = 0.0
                international = 0.0
                local = 0.0
                
                for source in project.funding_source_ids:
                    # Convert to project currency if needed
                    amount = source.amount
                    if source.currency_id != project.currency_id:
                        amount = source.currency_id._convert(
                            amount,
                            project.currency_id,
                            project.env.company,
                            fields.Date.today()
                        )
                    
                    total += amount
                    if source.funding_origin == 'international':
                        international += amount
                    elif source.funding_origin == 'local':
                        local += amount
                
                project.total_budget_computed = total
                project.total_international_funding = international
                project.total_local_funding = local
                project.funding_sources_count = len(project.funding_source_ids)
            else:
                project.total_budget_computed = 0.0
                project.total_international_funding = 0.0
                project.total_local_funding = 0.0
                project.funding_sources_count = 0
    
    @api.onchange('use_multi_source_funding')
    def _onchange_use_multi_source_funding(self):
        """Avertir l'utilisateur lors de l'activation du mode multi-sources."""
        if self.use_multi_source_funding and not self.funding_source_ids:
            return {
                'warning': {
                    'title': 'Mode Multi-Sources Activé',
                    'message': 'Aucune source de financement n\'existe encore. '
                              'Utilisez le bouton "Migrer les données existantes" pour '
                              'convertir vos données actuelles, ou ajoutez manuellement '
                              'des sources de financement dans l\'onglet dédié.'
                }
            }
    
    def action_view_funding_sources(self):
        """Ouvrir la vue des sources de financement."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sources de Financement',
            'res_model': 'sama.promis.project.funding.source',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_currency_id': self.currency_id.id,
            }
        }
    
    def action_enable_multi_source_funding(self):
        """Activer le mode multi-sources."""
        self.ensure_one()
        self.write({'use_multi_source_funding': True})
        
        # Si pas de sources et des contributions existent, suggérer la migration
        if not self.funding_source_ids and (self.donor_contribution > 0 or self.partner_contribution > 0):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Mode Multi-Sources Activé',
                    'message': 'Utilisez le bouton "Migrer les données existantes" pour convertir vos contributions actuelles.',
                    'type': 'info',
                    'sticky': False,
                }
            }
        return True
    
    def action_migrate_legacy_funding(self):
        """Migrer les données de financement héritées vers le nouveau système."""
        self.ensure_one()
        
        FundingSource = self.env['sama.promis.project.funding.source']
        sources_created = 0
        
        # Créer une source pour la contribution du bailleur
        if self.donor_contribution > 0 and self.donor_id:
            FundingSource.create({
                'name': f'Contribution {self.donor_id.name}',
                'project_id': self.id,
                'partner_id': self.donor_id.id,
                'amount': self.donor_contribution,
                'currency_id': self.currency_id.id,
                'funding_type': 'grant',
                'state': 'received',
                'sequence': 10,
            })
            sources_created += 1
        
        # Créer une source pour la contribution du partenaire
        if self.partner_contribution > 0 and self.partner_id:
            FundingSource.create({
                'name': f'Contribution {self.partner_id.name}',
                'project_id': self.id,
                'partner_id': self.partner_id.id,
                'amount': self.partner_contribution,
                'currency_id': self.currency_id.id,
                'funding_type': 'co_financing',
                'state': 'received',
                'sequence': 20,
            })
            sources_created += 1
        
        # Activer le mode multi-sources
        self.write({'use_multi_source_funding': True})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration Réussie',
                'message': f'{sources_created} source(s) de financement créée(s) avec succès.',
                'type': 'success',
                'sticky': False,
            }
        }

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

    def action_view_contracts(self):
        """Afficher les contrats liés au projet."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrats',
            'res_model': 'sama.promis.contract',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            }
        }

    def action_view_payments(self):
        """Afficher les paiements liés au projet."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Demandes de Paiement',
            'res_model': 'sama.promis.payment.request',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            }
        }

    def action_view_evaluations(self):
        """Afficher les évaluations liées au projet."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Évaluations',
            'res_model': 'sama.promis.project.evaluation',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            }
        }

    @api.depends('procurement_plan_ids')
    def _compute_procurement_plan_count(self):
        """Calcule le nombre de plans de passation de marché."""
        for project in self:
            project.procurement_plan_count = len(project.procurement_plan_ids)

    def action_view_procurement_plans(self):
        """Afficher les plans de passation de marché liés au projet."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plans de Passation de Marché',
            'res_model': 'sama.promis.procurement.plan',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_currency_id': self.currency_id.id,
                'default_plan_start_date': self.start_date,
                'default_plan_end_date': self.end_date,
            }
        }
    
    # Compliance Management Methods
    
    @api.depends('donor_id', 'donor_id.default_compliance_profile_id', 'compliance_profile_manual')
    def _compute_compliance_profile(self):
        """Compute compliance profile from donor or manual override."""
        for project in self:
            if project.compliance_profile_manual:
                project.compliance_profile_id = project.compliance_profile_manual
            elif project.donor_id and project.donor_id.default_compliance_profile_id:
                project.compliance_profile_id = project.donor_id.default_compliance_profile_id
            else:
                project.compliance_profile_id = False
    
    @api.depends('compliance_task_ids', 'compliance_task_ids.state', 'compliance_task_ids.is_overdue')
    def _compute_compliance_statistics(self):
        """Calculate compliance statistics."""
        for project in self:
            tasks = project.compliance_task_ids
            project.compliance_task_count = len(tasks)
            
            completed_tasks = tasks.filtered(lambda t: t.state in ['completed', 'approved'])
            project.compliance_tasks_completed = len(completed_tasks)
            
            if tasks:
                project.compliance_rate = (len(completed_tasks) / len(tasks)) * 100
            else:
                project.compliance_rate = 0.0
            
            overdue_tasks = tasks.filtered(lambda t: t.is_overdue)
            project.overdue_compliance_tasks = len(overdue_tasks)
    
    @api.depends('compliance_profile_id', 'compliance_profile_id.reporting_frequency', 
                 'last_compliance_report_date', 'start_date')
    def _compute_next_compliance_report_date(self):
        """Calculate next compliance report date."""
        for project in self:
            if not project.compliance_profile_id:
                project.next_compliance_report_date = False
                continue
            
            start_date = project.last_compliance_report_date or project.start_date
            if start_date:
                project.next_compliance_report_date = project.compliance_profile_id.calculate_next_report_date(start_date)
            else:
                project.next_compliance_report_date = False
    
    @api.depends('next_compliance_report_date')
    def _compute_compliance_report_status(self):
        """Calculate compliance report status."""
        from datetime import timedelta
        today = fields.Date.today()
        
        for project in self:
            if not project.next_compliance_report_date:
                project.compliance_report_status = False
                continue
            
            if project.next_compliance_report_date < today:
                project.compliance_report_status = 'overdue'
            elif (project.next_compliance_report_date - today).days <= 7:
                project.compliance_report_status = 'due_soon'
            else:
                project.compliance_report_status = 'on_time'
    
    @api.constrains('use_compliance_profile', 'compliance_profile_id', 'donor_id')
    def _check_compliance_profile(self):
        """Warn if compliance profile is not set when enabled."""
        for project in self:
            if project.use_compliance_profile and project.donor_id and not project.compliance_profile_id:
                # Just a warning, not blocking
                pass
    
    def action_view_compliance_tasks(self):
        """Open compliance tasks for this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tâches de Conformité - %s') % self.name,
            'res_model': 'sama.promis.compliance.task',
            'view_mode': 'tree,form,kanban,calendar',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'default_responsible_id': self.env.user.id,
            }
        }
    
    def action_generate_compliance_tasks(self):
        """Generate compliance tasks from compliance profile template."""
        self.ensure_one()
        
        if not self.compliance_profile_id:
            raise ValidationError(_('Aucun profil de conformité défini pour ce projet.'))
        
        # Get checklist items from profile
        checklist_items = self.compliance_profile_id.get_compliance_checklist_items()
        
        task_obj = self.env['sama.promis.compliance.task']
        created_tasks = task_obj
        
        # Create tasks from checklist
        for idx, item in enumerate(checklist_items):
            task_vals = {
                'name': item.get('name', f'Tâche {idx + 1}'),
                'description': item.get('description', ''),
                'project_id': self.id,
                'compliance_profile_id': self.compliance_profile_id.id,
                'task_type': item.get('type', 'other'),
                'priority': item.get('priority', 'normal'),
                'deadline': item.get('deadline', fields.Date.today()),
                'requires_document': item.get('requires_document', False),
                'requires_approval': item.get('requires_approval', False),
                'sequence': (idx + 1) * 10,
            }
            created_tasks |= task_obj.create(task_vals)
        
        if created_tasks:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Tâches Générées'),
                    'message': _('%d tâches de conformité ont été générées.') % len(created_tasks),
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        return True
    
    def action_submit_compliance_report(self):
        """Mark last compliance report date and recalculate next date."""
        self.ensure_one()
        
        self.write({
            'last_compliance_report_date': fields.Date.today()
        })
        
        # Create activity/notification
        self.message_post(
            body=_('Rapport de conformité soumis le %s') % fields.Date.today(),
            message_type='notification'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Rapport Soumis'),
                'message': _('Le rapport de conformité a été soumis avec succès.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_view_compliance_profile(self):
        """Open the compliance profile form view."""
        self.ensure_one()
        
        if not self.compliance_profile_id:
            raise ValidationError(_('Aucun profil de conformité défini.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Profil de Conformité'),
            'res_model': 'sama.promis.compliance.profile',
            'view_mode': 'form',
            'res_id': self.compliance_profile_id.id,
            'target': 'current',
        }
    
    @api.model
    def cron_send_report_reminders(self):
        """Cron job to send reminders for upcoming compliance reports."""
        from datetime import timedelta
        today = fields.Date.today()
        due_soon_date = today + timedelta(days=7)
        
        # Find projects with reports due soon
        projects = self.search([
            ('use_compliance_profile', '=', True),
            ('next_compliance_report_date', '!=', False),
            ('next_compliance_report_date', '<=', due_soon_date),
            ('state', 'in', ['in_progress', 'approved'])
        ])
        
        template = self.env.ref('sama_promis.mail_template_compliance_report_reminder', raise_if_not_found=False)
        
        for project in projects:
            if template and project.created_by:
                template.send_mail(project.id, force_send=True)
        
        return True
    
    @api.model
    def cron_update_compliance_statistics(self):
        """Cron job to update compliance statistics for all active projects."""
        projects = self.search([
            ('use_compliance_profile', '=', True),
            ('state', 'in', ['draft', 'in_progress', 'approved'])
        ])
        
        # Force recomputation
        projects._compute_compliance_statistics()
        projects._compute_compliance_report_status()
        
        return True