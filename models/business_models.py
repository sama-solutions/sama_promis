from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GovernmentProject(models.Model):
    _name = 'government.project'
    _description = 'Projet Gouvernemental - Plan Sénégal 2050'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project_code desc'

    # Numérotation automatique Plan Sénégal 2050
    project_code = fields.Char(
        string="Code Projet SN-2050", 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: self._get_next_project_code()
    )
    
    name = fields.Char(string="Nom du Projet", required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    start_date = fields.Date(string="Date de Début", readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string="Date de Fin", readonly=True, states={'draft': [('readonly', False)]})
    
    # Statut aligné sur Plan Sénégal 2050
    status = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('in_progress', 'En Cours'),
        ('suspended', 'Suspendu'),
        ('completed', 'Achevé'),
        ('cancelled', 'Annulé')
    ], string="Statut", default='draft', tracking=True)
    
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})
    
    strategic_objective_id = fields.Many2one('strategic.objective', string="Objectif Stratégique", required=True)
    budget_id = fields.Many2one('government.budget', string="Budget Alloué")
    ministry_id = fields.Many2one('government.ministry', string="Ministère Responsable")
    manager_id = fields.Many2one('res.users', string="Chef de Projet")
    
    # Connexion avec le module projet d'Odoo
    odoo_project_id = fields.Many2one(
        'project.project', 
        string="Projet Odoo Associé",
        help="Projet Odoo créé automatiquement pour la gestion opérationnelle"
    )
    
    # Priorité selon Plan Sénégal 2050
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Importante'),
        ('2', 'Urgente'),
        ('3', 'Critique')
    ], string="Priorité", default='0')

    # Geolocation
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    # Informations sur l'avancement
    progress = fields.Float(string="Pourcentage d'avancement", compute='_compute_progress', store=True)
    task_count = fields.Integer(string="Nombre de tâches", compute='_compute_task_count')
    
    @api.model
    def _get_next_project_code(self):
        """Génère le prochain code de projet au format SN-2050-XXXXX"""
        # Rechercher le dernier numéro utilisé
        last_project = self.search([], order='id desc', limit=1)
        if last_project and last_project.project_code:
            try:
                # Extraire le numéro depuis le code existant
                code_parts = last_project.project_code.split('-')
                if len(code_parts) == 3 and code_parts[0] == 'SN' and code_parts[1] == '2050':
                    last_number = int(code_parts[2])
                    next_number = last_number + 1
                else:
                    next_number = 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"SN-2050-{next_number:05d}"
    
    @api.depends('odoo_project_id.tasks')
    def _compute_task_count(self):
        """Calcule le nombre de tâches du projet Odoo associé"""
        for record in self:
            if record.odoo_project_id:
                record.task_count = len(record.odoo_project_id.tasks)
            else:
                record.task_count = 0
    
    @api.depends('odoo_project_id.tasks.stage_id')
    def _compute_progress(self):
        """Calcule le pourcentage d'avancement basé sur les tâches Odoo"""
        for record in self:
            if record.odoo_project_id and record.odoo_project_id.tasks:
                total_tasks = len(record.odoo_project_id.tasks)
                # Dans Odoo 18, utiliser fold pour identifier les étapes fermées
                completed_tasks = len(record.odoo_project_id.tasks.filtered(lambda t: t.stage_id and t.stage_id.fold))
                record.progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0
            else:
                record.progress = 0.0
    
    @api.model
    def create(self, vals_list):
        """Surcharge de la création pour générer automatiquement le code projet"""
        # Gérer le cas où vals_list est un dictionnaire unique (compatibilité)
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        # Générer les codes projet pour chaque enregistrement
        for vals in vals_list:
            if not vals.get('project_code'):
                vals['project_code'] = self._get_next_project_code()
        
        records = super(GovernmentProject, self).create(vals_list)
        return records
    
    def create_odoo_project(self):
        """Crée un projet Odoo associé pour la gestion opérationnelle"""
        for record in self:
            if not record.odoo_project_id:
                project_vals = {
                    'name': f"[{record.project_code}] {record.name}",
                    'description': record.description,
                    'date_start': record.start_date,
                    'date': record.end_date,
                    'user_id': record.manager_id.id if record.manager_id else False,
                    'privacy_visibility': 'employees',  # Visible aux employés
                    'active': True,
                }
                
                odoo_project = self.env['project.project'].create(project_vals)
                record.odoo_project_id = odoo_project.id
                
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projet Odoo Créé',
            'res_model': 'project.project',
            'res_id': self.odoo_project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def sync_with_odoo_project(self):
        """Synchronise les données avec le projet Odoo associé"""
        for record in self:
            if record.odoo_project_id:
                # Synchroniser les informations de base
                record.odoo_project_id.write({
                    'name': f"[{record.project_code}] {record.name}",
                    'description': record.description,
                    'date_start': record.start_date,
                    'date': record.end_date,
                    'user_id': record.manager_id.id if record.manager_id else False,
                })
    
    def action_validate(self):
        """Valide le projet et crée automatiquement le projet Odoo associé"""
        for record in self:
            record.status = 'validated'
            if not record.odoo_project_id:
                record.create_odoo_project()
    
    def action_start(self):
        """Démarre le projet"""
        for record in self:
            record.status = 'in_progress'
            record.sync_with_odoo_project()
    
    def action_suspend(self):
        """Suspend le projet"""
        for record in self:
            record.status = 'suspended'
    
    def action_complete(self):
        """Marque le projet comme achevé"""
        for record in self:
            record.status = 'completed'
    
    def action_cancel(self):
        """Annule le projet"""
        for record in self:
            record.status = 'cancelled'
    
    def action_reset_to_draft(self):
        """Remet le projet en brouillon"""
        for record in self:
            record.status = 'draft'

    @api.model
    def action_validate_by_xmlid(self, xml_id):
        """Valide un projet par son XML ID"""
        project = self.env.ref(xml_id)
        if project:
            project.action_validate()
        else:
            raise ValidationError(f"Projet avec XML ID {xml_id} non trouvé.")

    def action_open_odoo_project(self):
        """Ouvre le projet Odoo associé"""
        self.ensure_one()
        if not self.odoo_project_id:
            raise ValidationError("Aucun projet Odoo associé. Veuillez d'abord valider le projet.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projet Odoo - {self.project_code}',
            'res_model': 'project.project',
            'res_id': self.odoo_project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_open_odoo_tasks(self):
        """Ouvre les tâches du projet Odoo associé"""
        self.ensure_one()
        if not self.odoo_project_id:
            raise ValidationError("Aucun projet Odoo associé. Veuillez d'abord valider le projet.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tâches - {self.project_code}',
            'res_model': 'project.task',
            'view_mode': 'list,form,kanban',
            'views': [(self.env.ref('project.view_task_tree2').id, 'list'),
                      (self.env.ref('project.view_task_form2').id, 'form'),
                      (self.env.ref('project.view_task_kanban').id, 'kanban')],
            'domain': [('project_id', '=', self.odoo_project_id.id)],
            'context': {
                'default_project_id': self.odoo_project_id.id,
                'search_default_project_id': self.odoo_project_id.id,
            },
            'target': 'current',
        }
    
    def get_public_url(self):
        """Retourne l'URL publique du projet"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/senegal2050/project/{self.id}"
    
    def get_qr_code_url(self):
        """Retourne l'URL pour générer le QR code du projet"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/senegal2050/qr/government.project/{self.id}"
    
    def action_share_public(self):
        """Action pour partager publiquement le projet"""
        self.ensure_one()
        public_url = self.get_public_url()
        return {
            'type': 'ir.actions.act_url',
            'url': public_url,
            'target': 'new',
        }

class GovernmentDecision(models.Model):
    _name = 'government.decision'
    _description = 'Décision Officielle'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom", compute='_compute_name', store=True)
    title = fields.Char(string="Titre", required=True, tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    reference = fields.Char(string="Référence", readonly=True, states={'draft': [('readonly', False)]})
    decision_type = fields.Selection([
        ('decree', 'Décret'),
        ('order', 'Arrêté'),
        ('circular', 'Circulaire'),
        ('instruction', 'Instruction'),
        ('other', 'Autre')
    ], string="Type de Décision", default='decree', readonly=True, states={'draft': [('readonly', False)]})
    decision_date = fields.Date(string="Date de la Décision", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    document = fields.Binary(string="Document", readonly=True, states={'draft': [('readonly', False)]})
    document_name = fields.Char(string="Nom du Document", readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Selection([
        ('draft', 'Brouillon'),
        ('published', 'Publiée'),
        ('archived', 'Archivée')
    ], string="Statut", default='draft', tracking=True)
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)
    strategic_objective_id = fields.Many2one('strategic.objective', string="Objectif Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('government.project', string="Projet Associé", readonly=True, states={'draft': [('readonly', False)]})
    event_id = fields.Many2one('government.event', string="Événement Associé", readonly=True, states={'draft': [('readonly', False)]})
    ministry_id = fields.Many2one('government.ministry', string="Ministère Émetteur", readonly=True, states={'draft': [('readonly', False)]})
    is_public = fields.Boolean(string="Public", default=False, readonly=True, states={'draft': [('readonly', False)]})
    
    # Système de suivi des décisions
    implementation_status = fields.Selection([
        ('not_started', 'Non Commencée'),
        ('in_progress', 'En Cours'),
        ('partially_completed', 'Partiellement Réalisée'),
        ('completed', 'Réalisée'),
        ('delayed', 'Retardée'),
        ('blocked', 'Bloquée')
    ], string="État de Mise en Œuvre", default='not_started', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    
    implementation_deadline = fields.Date(string="Échéance de Mise en Œuvre", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    responsible_user_id = fields.Many2one('res.users', string="Responsable de Suivi", readonly=True, states={'draft': [('readonly', False)]})
    progress_percentage = fields.Float(string="Pourcentage d'Avancement", default=0.0, help="Pourcentage d'avancement de la mise en œuvre", readonly=True, states={'draft': [('readonly', False)]})
    
    # Champs pour les rapports de suivi
    last_follow_up_date = fields.Date(string="Dernière Date de Suivi", readonly=True, states={'draft': [('readonly', False)]})
    next_follow_up_date = fields.Date(string="Prochaine Date de Suivi", readonly=True, states={'draft': [('readonly', False)]})
    follow_up_notes = fields.Text(string="Notes de Suivi", readonly=True, states={'draft': [('readonly', False)]})
    
    # Indicateurs de performance
    is_on_track = fields.Boolean(string="Dans les Temps", compute='_compute_is_on_track', store=True)
    days_until_deadline = fields.Integer(string="Jours Avant Échéance", compute='_compute_days_until_deadline', store=True)

    # Geolocation
    latitude = fields.Float(string='Latitude', digits=(10, 7), readonly=True, states={'draft': [('readonly', False)]})
    longitude = fields.Float(string='Longitude', digits=(10, 7), readonly=True, states={'draft': [('readonly', False)]})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})
    
    @api.depends('implementation_deadline', 'implementation_status')
    def _compute_is_on_track(self):
        from datetime import date
        for record in self:
            if record.implementation_deadline and record.implementation_status not in ['completed', 'blocked']:
                days_left = (record.implementation_deadline - date.today()).days
                # Considérer comme "dans les temps" si plus de 30 jours restants ou déjà terminé
                record.is_on_track = days_left > 30 or record.implementation_status == 'completed'
            else:
                record.is_on_track = record.implementation_status == 'completed'
    
    @api.depends('implementation_deadline')
    def _compute_days_until_deadline(self):
        from datetime import date
        for record in self:
            if record.implementation_deadline:
                record.days_until_deadline = (record.implementation_deadline - date.today()).days
            else:
                record.days_until_deadline = 0
    
    def action_start_implementation(self):
        """Démarre la mise en œuvre de la décision"""
        for record in self:
            record.implementation_status = 'in_progress'
            record.last_follow_up_date = fields.Date.today()
    
    def action_complete_implementation(self):
        """Marque la décision comme complètement mise en œuvre"""
        for record in self:
            record.implementation_status = 'completed'
            record.progress_percentage = 100.0
            record.last_follow_up_date = fields.Date.today()
    
    def action_mark_delayed(self):
        """Marque la décision comme retardée"""
        for record in self:
            record.implementation_status = 'delayed'
            record.last_follow_up_date = fields.Date.today()
    
    def action_mark_blocked(self):
        """Marque la décision comme bloquée"""
        for record in self:
            record.implementation_status = 'blocked'
            record.last_follow_up_date = fields.Date.today()
    
    def action_create_follow_up_task(self):
        """Crée une tâche de suivi dans Odoo"""
        self.ensure_one()
        task_vals = {
            'name': f"Suivi Décision: {self.title}",
            'description': f"Suivi de la mise en œuvre de la décision {self.reference}\n\nDécision: {self.title}\nÉchéance: {self.implementation_deadline}\nStatut actuel: {dict(self._fields['implementation_status'].selection)[self.implementation_status]}",
            'user_ids': [(6, 0, [self.responsible_user_id.id])] if self.responsible_user_id else [],
            'date_deadline': self.next_follow_up_date or self.implementation_deadline,
            'project_id': self.project_id.odoo_project_id.id if self.project_id and self.project_id.odoo_project_id else False,
        }
        
        task = self.env['project.task'].create(task_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tâche de Suivi Créée',
            'res_model': 'project.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.depends('title', 'reference')
    def _compute_name(self):
        for record in self:
            if record.reference and record.title:
                record.name = f"[{record.reference}] {record.title}"
            else:
                record.name = record.title or record.reference or "Nouvelle décision"

class GovernmentEvent(models.Model):
    _name = 'government.event'
    _description = 'Événement Public'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Geolocation
    latitude = fields.Float(string='Latitude', digits=(10, 7), readonly=True, states={'draft': [('readonly', False)]})
    longitude = fields.Float(string='Longitude', digits=(10, 7), readonly=True, states={'draft': [('readonly', False)]})

    name = fields.Char(string="Nom de l'Événement", required=True, tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    event_date = fields.Date(string="Date de l'Événement", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    date_start = fields.Datetime(string="Date et Heure de Début", readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Datetime(string="Date et Heure de Fin", readonly=True, states={'draft': [('readonly', False)]})
    location = fields.Char(string="Lieu", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    organizer_id = fields.Many2one('government.ministry', string="Organisateur", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    event_type = fields.Selection([
        ('meeting', 'Réunion'),
        ('conference', 'Conférence'),
        ('workshop', 'Atelier'),
        ('ceremony', 'Cérémonie'),
        ('launch', 'Lancement'),
        ('other', 'Autre')
    ], string="Type d'Événement", default='meeting', readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('government.project', string="Projet Associé", readonly=True, states={'draft': [('readonly', False)]})
    strategic_objective_id = fields.Many2one('strategic.objective', string="Objectif Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifié'),
        ('validated', 'Validé'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string="Statut", default='draft', tracking=True)
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='draft', readonly=True, copy=False)
    
    # Liaison avec les événements Odoo (module calendar)
    odoo_event_id = fields.Many2one(
        'calendar.event', 
        string="Événement Odoo Associé",
        help="Événement Odoo créé automatiquement pour la gestion du calendrier"
    )

    def action_set_to_draft(self):
        """Remet l'événement en brouillon pour modification"""
        for record in self:
            record.write({
                'state': 'draft',
                'status': 'draft'
            })

    def action_set_to_locked(self):
        """Verrouille l'événement après modification"""
        self.write({'state': 'locked'})
    
    def action_start(self):
        """Démarre l'événement (passe en cours)"""
        for record in self:
            if record.status == 'validated':
                record.status = 'ongoing'
    
    def action_complete(self):
        """Marque l'événement comme terminé"""
        for record in self:
            if record.status == 'ongoing':
                record.status = 'completed'
    
    def create_odoo_event(self):
        """Crée un événement Odoo associé pour la gestion calendaire"""
        for record in self:
            if not record.odoo_event_id:
                event_vals = {
                    'name': record.name,
                    'description': record.description,
                    'start': record.date_start,
                    'stop': record.date_end,
                    'location': record.location,
                    'privacy': 'public',  # Événement public
                    'show_as': 'busy',
                }
                
                odoo_event = self.env['calendar.event'].create(event_vals)
                record.odoo_event_id = odoo_event.id
                
        return {
            'type': 'ir.actions.act_window',
            'name': 'Événement Odoo Créé',
            'res_model': 'calendar.event',
            'res_id': self.odoo_event_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_validate(self):
        """Valide l'événement et crée automatiquement l'événement Odoo associé"""
        for record in self:
            if record.status == 'draft':
                record.status = 'validated'
                if not record.odoo_event_id:
                    record.create_odoo_event()
    
    def action_open_public_profile(self):
        """Ouvre la page publique de l'événement"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': f'{base_url}/senegal2050/event/{self.id}',
            'target': 'new',
        }
    
    def action_open_odoo_event(self):
        """Ouvre l'événement Odoo associé dans le calendrier"""
        self.ensure_one()
        if not self.odoo_event_id:
            raise ValidationError("Aucun événement Odoo associé. Veuillez d'abord valider l'événement.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Événement Odoo - {self.name}',
            'res_model': 'calendar.event',
            'res_id': self.odoo_event_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def sync_with_odoo_event(self):
        """Synchronise les données avec l'événement Odoo associé"""
        for record in self:
            if record.odoo_event_id:
                # Synchroniser les informations de base
                record.odoo_event_id.write({
                    'name': record.name,
                    'description': record.description,
                    'start': record.date_start,
                    'stop': record.date_end,
                    'location': record.location,
                })

class GovernmentBudget(models.Model):
    _name = 'government.budget'
    _description = "Budget d'Investissement/Fonctionnement"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom du Budget", required=True, tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    fiscal_year = fields.Char(string="Année Fiscale", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    total_amount = fields.Monetary(string="Montant Total", currency_field='currency_id', compute='_compute_total_amount', store=True)
    allocated_amount = fields.Monetary(string="Montant Alloué", currency_field='currency_id', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    used_amount = fields.Monetary(string="Montant Utilisé", currency_field='currency_id', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    remaining_amount = fields.Monetary(string="Montant Restant", currency_field='currency_id', compute='_compute_remaining_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self._get_default_currency(), readonly=True, states={'draft': [('readonly', False)]})

    @api.model
    def _get_default_currency(self):
        """Retourne la devise CFA (XOF) par défaut"""
        xof_currency = self.env['res.currency'].search([('name', '=', 'XOF')], limit=1)
        return xof_currency or self.env.company.currency_id
    budget_type = fields.Selection([
        ('investment', 'Investissement'),
        ('operating', 'Fonctionnement'),
        ('emergency', 'Urgence')
    ], string="Type de Budget", default='investment', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Selection([
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('active', 'Actif'),
        ('closed', 'Clôturé')
    ], string="Statut", default='draft', tracking=True)
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)
    ministry_id = fields.Many2one('government.ministry', string="Ministère Bénéficiaire", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    strategic_objective_id = fields.Many2one('strategic.objective', string="Objectif Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    
    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})
    
    @api.depends('allocated_amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.allocated_amount
    
    @api.depends('allocated_amount', 'used_amount')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.allocated_amount - record.used_amount
