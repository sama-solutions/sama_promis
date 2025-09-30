# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import json

class SamaPromisContract(models.Model):
    _name = 'sama.promis.contract'
    _description = 'Contrat SAMA PROMIS'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Référence du Contrat", required=True, tracking=True)
    project_id = fields.Many2one('sama.promis.project', string="Projet",
                               required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string="Bénéficiaire",
                               required=True, tracking=True)

    # Contract Details
    contract_type = fields.Selection([
        ('grant', 'Subvention'),
        ('service', 'Prestation de Service'),
        ('partnership', 'Partenariat'),
        ('other', 'Autre'),
    ], string="Type de Contrat", required=True, tracking=True)

    start_date = fields.Date(string="Date de Début", tracking=True)
    end_date = fields.Date(string="Date de Fin", tracking=True)
    amount = fields.Monetary(string="Montant du Contrat",
                           currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency',
                                default=lambda self: self.env.company.currency_id)

    # Enhanced Contract Management
    contract_template_id = fields.Many2one('sama.promis.contract.template', 
                                         string="Modèle de Contrat",
                                         tracking=True)
    contract_content_html = fields.Html(string="Contenu du Contrat", 
                                       compute='_compute_contract_content',
                                       store=True)
    
    # Electronic Signature Integration (Optional - requires sign module)
    sign_request_id = fields.Many2one('sign.request', string="Demande de Signature", 
                                     readonly=True, tracking=True)
    signed_document_id = fields.Many2one('ir.attachment', string="Document Signé", 
                                        readonly=True)
    
    # Document Management
    contract_document = fields.Binary(string="Document du Contrat",
                                    attachment=True)
    contract_filename = fields.Char(string="Nom du Fichier du Contrat")

    # Enhanced Signature Status
    signature_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('generated', 'Généré'),
        ('sent_for_signature', 'Envoyé pour Signature'),
        ('partially_signed', 'Partiellement Signé'),
        ('signed', 'Signé'),
        ('refused', 'Refusé'),
        ('expired', 'Expiré'),
    ], string="État de la Signature", default='draft', tracking=True)

    # Status
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('generated', 'Généré'),
        ('ready', 'Prêt pour Signature'),
        ('sent_for_signature', 'Envoyé pour Signature'),
        ('signed', 'Signé'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('terminated', 'Résilié'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', tracking=True)

    # Payment Schedule
    payment_schedule_ids = fields.One2many('sama.promis.payment.schedule',
                                         'contract_id',
                                         string="Échéancier de Paiement")

    # Additional Fields for Enhanced Functionality
    
    # Contract Terms and Conditions
    terms_conditions = fields.Html(string="Conditions Générales")
    special_conditions = fields.Text(string="Conditions Spéciales")
    
    # Compliance and Reporting
    reporting_frequency = fields.Selection([
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('semi_annual', 'Semestriel'),
        ('annual', 'Annuel'),
    ], string="Fréquence de Rapportage", default='quarterly')
    
    next_report_date = fields.Date(
        string="Prochaine Date de Rapport",
        compute='_compute_next_report_date',
        store=True,
        help="Prochaine date de rapport calculée"
    )

    procurement_plan_ids = fields.One2many(
        'sama.promis.procurement.plan',
        'contract_id',
        string='Plans de Passation de Marché',
        help="Plans de passation de marché liés à ce contrat"
    )

    procurement_plan_count = fields.Integer(
        string='Nombre de Plans de Passation',
        compute='_compute_procurement_plan_count',
        store=False
    )
    
    # Compliance Profile (inherited from project)
    compliance_profile_id = fields.Many2one(
        'sama.promis.compliance.profile',
        string='Profil de Conformité',
        related='project_id.compliance_profile_id',
        store=True,
        help="Profil de conformité hérité du projet"
    )
    use_compliance_profile = fields.Boolean(
        string='Utiliser Conformité',
        related='project_id.use_compliance_profile',
        help="Activer la gestion de conformité (hérité du projet)"
    )
    
    # Compliance Tasks
    compliance_task_ids = fields.One2many(
        'sama.promis.compliance.task',
        'contract_id',
        string='Tâches de Conformité',
        help="Tâches de conformité spécifiques au contrat"
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
    compliance_report_status = fields.Selection([
        ('on_time', 'À Jour'),
        ('due_soon', 'Échéance Proche'),
        ('overdue', 'En Retard')
    ], string='Statut Rapport',
        compute='_compute_compliance_report_status',
        help="Statut du rapport de conformité")

    _sql_constraints = [
        ('check_dates', 'CHECK(start_date <= end_date)',
         "La date de début doit être antérieure ou égale à la date de fin.")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code('sama.promis.contract') or _('New')
        return super().create(vals_list)

    @api.depends('project_id', 'partner_id', 'contract_template_id', 'amount', 'start_date', 'end_date')
    def _compute_contract_content(self):
        """Compute contract content based on template and project data"""
        for contract in self:
            if contract.contract_template_id and contract.project_id and contract.partner_id:
                # Get template content
                template_content = contract.contract_template_id.html_content or ''
                
                # Replace placeholders with actual data
                content = template_content
                
                # Basic replacements
                replacements = {
                    '{{ contract.reference }}': contract.name,
                    '{{ project.title }}': contract.project_id.name,
                    '{{ project.description }}': contract.project_id.description or '',
                    '{{ grantee.name }}': contract.partner_id.name,
                    '{{ grantee.address }}': contract.partner_id.contact_address or '',
                    '{{ contract.amount }}': f"{contract.amount:,.2f} {contract.currency_id.name}" if contract.amount else '',
                    '{{ contract.start_date }}': contract.start_date.strftime('%d/%m/%Y') if contract.start_date else '',
                    '{{ contract.end_date }}': contract.end_date.strftime('%d/%m/%Y') if contract.end_date else '',
                    '{{ donor.name }}': contract.project_id.donor_id.name if contract.project_id and contract.project_id.donor_id else '',
                }
                
                for placeholder, value in replacements.items():
                    content = content.replace(placeholder, str(value))
                
                # Add payment schedule table if exists
                if contract.payment_schedule_ids:
                    payment_table = self._generate_payment_schedule_table()
                    content = content.replace('{{ payment_schedule_table }}', payment_table)
                
                contract.contract_content_html = content
            else:
                contract.contract_content_html = ''

    def _generate_payment_schedule_table(self):
        """Generate HTML table for payment schedule"""
        if not self.payment_schedule_ids:
            return '<p>Aucun échéancier de paiement défini.</p>'
        
        table_html = '''
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Référence</th>
                    <th>Date d'Échéance</th>
                    <th>Montant</th>
                    <th>Pourcentage</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for schedule in self.payment_schedule_ids:
            table_html += f'''
                <tr>
                    <td>{schedule.name}</td>
                    <td>{schedule.due_date.strftime('%d/%m/%Y') if schedule.due_date else ''}</td>
                    <td>{schedule.amount:,.2f} {self.currency_id.name}</td>
                    <td>{schedule.payment_percentage:.1f}%</td>
                    <td>{schedule.description or ''}</td>
                </tr>
            '''
        
        table_html += '</tbody></table>'
        return table_html

    def action_generate_contract(self):
        """Generate contract document with enhanced functionality"""
        self.ensure_one()
        
        if not self.contract_template_id:
            raise UserError(_("Veuillez sélectionner un modèle de contrat."))
        
        if not self.contract_content_html:
            raise UserError(_("Impossible de générer le contenu du contrat. Vérifiez les données du projet et du bénéficiaire."))

        # Generate PDF using QWeb report
        report_action = self.env.ref('sama_promis.report_sama_promis_contract')
        pdf_content, _ = report_action._render_qweb_pdf(self.id)
        
        self.write({
            'contract_document': base64.b64encode(pdf_content),
            'contract_filename': f"contract_{self.name}.pdf",
            'state': 'generated',
            'signature_status': 'generated',
        })

        # Send notification
        self.message_post(
            body=_("Le contrat %s a été généré avec succès.") % self.name,
            subject=_("Contrat Généré"),
            message_type='notification'
        )
        
        # Generate initial compliance tasks if compliance profile exists
        if self.compliance_profile_id and not self.compliance_task_ids:
            self.action_generate_compliance_tasks()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sama.promis.contract',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'context': {'success_message': _("Le contrat a été généré avec succès.")}
        }

    def _generate_pdf_content(self):
        """Generate PDF content using QWeb report"""
        report_action = self.env.ref('sama_promis.report_sama_promis_contract')
        pdf_content, _ = report_action._render_qweb_pdf(self.id)
        return pdf_content

    def action_send_for_signature(self):
        """Send contract for electronic signature"""
        self.ensure_one()
        
        if self.state != 'generated':
            raise UserError(_("Le contrat doit être généré avant d'être envoyé pour signature."))
        
        if not self.contract_document:
            raise UserError(_("Le document du contrat n'a pas été généré. Veuillez d'abord générer le contrat."))

        # Check if sign module is available
        if not self.env['ir.module.module'].search([('name', '=', 'sign'), ('state', '=', 'installed')]):
            raise UserError(_("Le module de signature électronique n'est pas installé. Veuillez l'installer pour utiliser cette fonctionnalité."))

        # Use the already generated PDF document
        pdf_content = base64.b64decode(self.contract_document)
        
        # Create signature request
        sign_template_id = self.contract_template_id.sign_template_id.id if self.contract_template_id.sign_template_id else False
        
        # If no sign template is defined, create a basic one
        if not sign_template_id:
            # Create attachment for the template
            attachment = self.env['ir.attachment'].create({
                'name': f"{self.name}_template.pdf",
                'datas': self.contract_document,
                'res_model': 'sama.promis.contract',
                'res_id': self.id,
            })
            
            # Create sign template
            sign_template = self.env['sign.template'].create({
                'name': f"Template for {self.name}",
                'attachment_id': attachment.id,
            })
            
            # Create sign items (signature fields)
            # For the beneficiary
            self.env['sign.item'].create({
                'template_id': sign_template.id,
                'type_id': self.env.ref('sign.sign_item_type_signature').id,
                'name': 'Signature Bénéficiaire',
                'responsible_id': self.env.ref('sign.sign_lead_role').id,
                'page': 1,
                'posX': 0.2,
                'posY': 0.8,
                'width': 0.2,
                'height': 0.05,
            })
            
            # For the donor/manager
            self.env['sign.item'].create({
                'template_id': sign_template.id,
                'type_id': self.env.ref('sign.sign_item_type_signature').id,
                'name': 'Signature Bailleur',
                'responsible_id': self.env.ref('sign.sign_manager_role').id,
                'page': 1,
                'posX': 0.7,
                'posY': 0.8,
                'width': 0.2,
                'height': 0.05,
            })
            
            sign_template_id = sign_template.id
        
        # Create signature request
        sign_request = self.env['sign.request'].create({
            'template_id': sign_template_id,
            'reference': self.name,
            'request_item_ids': [
                (0, 0, {
                    'partner_id': self.partner_id.id,
                    'role_id': self.env.ref('sign.sign_lead_role').id if self.env.ref('sign.sign_lead_role', raise_if_not_found=False) else False,
                }),
                (0, 0, {
                    'partner_id': self.env.user.partner_id.id,
                    'role_id': self.env.ref('sign.sign_manager_role').id if self.env.ref('sign.sign_manager_role', raise_if_not_found=False) else False,
                }),
            ],
            'attachment_ids': [(0, 0, {
                'name': f"{self.name}.pdf",
                'datas': self.contract_document,
                'res_model': 'sama.promis.contract',
                'res_id': self.id,
            })],
        })
        
        # Send the signature request
        if hasattr(sign_request, 'action_sent'):
            sign_request.action_sent()

        # Update contract state
        self.write({
            'sign_request_id': sign_request.id,
            'state': 'sent_for_signature',
            'signature_status': 'sent_for_signature',
        })
        
        # Send notification
        self.message_post(
            body=_("Le contrat %s a été envoyé pour signature électronique.") % self.name,
            subject=_("Contrat Envoyé pour Signature"),
            message_type='notification'
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sama.promis.contract',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'context': {'success_message': _("Le contrat a été envoyé pour signature électronique.")}
        }

    def action_mark_signed(self):
        """Mark contract as signed (manual process for CE)"""
        self.ensure_one()
        if not self.contract_document:
            raise UserError(_("Veuillez d'abord générer le document de contrat."))

        self.write({
            'state': 'signed',
            'signature_status': 'signed',
        })

        # Send notification
        self.message_post(
            body=_("Contract %s has been marked as signed.") % self.name,
            subject=_("Contract Signed"),
            message_type='notification'
        )

        return True

    def action_download_contract(self):
        """Download the contract document"""
        self.ensure_one()
        if not self.contract_document:
            raise UserError(_("Aucun document de contrat généré."))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=sama.promis.contract&id={self.id}&field=contract_document&download=true&filename={self.contract_filename}',
            'target': 'self',
        }

    @api.model
    def _check_signature_status(self):
        """Cron job to check signature status"""
        contracts = self.search([('state', '=', 'sent_for_signature')])
        for contract in contracts:
            if contract.sign_request_id:
                if contract.sign_request_id.state == 'signed':
                    contract.write({
                        'state': 'signed',
                        'signature_status': 'signed',
                        'signed_document_id': contract.sign_request_id.signed_document_id.id if contract.sign_request_id.signed_document_id else False,
                    })
                elif contract.sign_request_id.state == 'refused':
                    contract.write({
                        'signature_status': 'refused',
                    })



class SamaPromisPaymentSchedule(models.Model):
    _name = 'sama.promis.payment.schedule'
    _description = "Échéancier de Paiement"
    _order = 'due_date'

    name = fields.Char(string="Référence", required=True)
    contract_id = fields.Many2one('sama.promis.contract',
                                string="Contrat",
                                ondelete='cascade')
    due_date = fields.Date(string="Date d'Échéance", required=True)
    amount = fields.Monetary(string="Montant",
                           currency_field='currency_id',
                           required=True)
    currency_id = fields.Many2one(related='contract_id.currency_id',
                                string="Devise",
                                store=True)
    payment_percentage = fields.Float(string="Pourcentage du Total")
    description = fields.Text(string="Description")

    # Payment tracking
    # Note: account.payment integration disabled - requires 'account' module (Enterprise)
    # payment_id = fields.Many2one('account.payment',
    #                            string="Paiement Réalisé",
    #                            readonly=True)
    # payment_state = fields.Selection(related='payment_id.state',
    #                                string="État du Paiement",
    #                                store=True)
    
    # Alternative CE-compatible payment tracking
    payment_reference = fields.Char(string="Référence de Paiement")
    payment_state = fields.Selection([
        ('not_paid', 'Non Payé'),
        ('partial', 'Partiellement Payé'),
        ('paid', 'Payé'),
    ], string="État du Paiement", default='not_paid')

    @api.onchange('amount', 'contract_id.amount')
    def _onchange_amount(self):
        for record in self:
            if record.contract_id and record.contract_id.amount != 0:
                record.payment_percentage = (record.amount / record.contract_id.amount) * 100

    @api.depends('procurement_plan_ids')
    def _compute_procurement_plan_count(self):
        """Calcule le nombre de plans de passation de marché."""
        for contract in self:
            contract.procurement_plan_count = len(contract.procurement_plan_ids)

    def action_view_procurement_plans(self):
        """Afficher les plans de passation de marché liés au contrat."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plans de Passation de Marché',
            'res_model': 'sama.promis.procurement.plan',
            'view_mode': 'tree,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {
                'default_contract_id': self.id,
                'default_project_id': self.project_id.id,
                'default_currency_id': self.currency_id.id,
                'default_plan_start_date': self.start_date,
                'default_plan_end_date': self.end_date,
            }
        }
    
    # Compliance Management Methods
    
    @api.depends('compliance_task_ids', 'compliance_task_ids.state', 'compliance_task_ids.is_overdue')
    def _compute_compliance_statistics(self):
        """Calculate compliance statistics."""
        for contract in self:
            tasks = contract.compliance_task_ids
            contract.compliance_task_count = len(tasks)
            
            completed_tasks = tasks.filtered(lambda t: t.state in ['completed', 'approved'])
            contract.compliance_tasks_completed = len(completed_tasks)
            
            if tasks:
                contract.compliance_rate = (len(completed_tasks) / len(tasks)) * 100
            else:
                contract.compliance_rate = 0.0
            
            overdue_tasks = tasks.filtered(lambda t: t.is_overdue)
            contract.overdue_compliance_tasks = len(overdue_tasks)
    
    @api.depends('compliance_profile_id', 'compliance_profile_id.reporting_frequency',
                 'last_compliance_report_date', 'reporting_frequency', 'start_date')
    def _compute_next_report_date(self):
        """Calculate next report date based on reporting frequency or compliance profile."""
        from dateutil.relativedelta import relativedelta
        from datetime import timedelta
        
        for contract in self:
            # Use compliance profile if available
            if contract.compliance_profile_id:
                start_date = contract.last_compliance_report_date or contract.start_date
                if start_date:
                    contract.next_report_date = contract.compliance_profile_id.calculate_next_report_date(start_date)
                else:
                    contract.next_report_date = False
            # Otherwise use contract's own reporting frequency
            elif contract.reporting_frequency and contract.start_date:
                start_date = contract.last_compliance_report_date or contract.start_date
                
                if contract.reporting_frequency == 'monthly':
                    contract.next_report_date = start_date + relativedelta(months=1)
                elif contract.reporting_frequency == 'quarterly':
                    contract.next_report_date = start_date + relativedelta(months=3)
                elif contract.reporting_frequency == 'semi_annual':
                    contract.next_report_date = start_date + relativedelta(months=6)
                elif contract.reporting_frequency == 'annual':
                    contract.next_report_date = start_date + relativedelta(years=1)
                else:
                    contract.next_report_date = False
            else:
                contract.next_report_date = False
    
    @api.depends('next_report_date')
    def _compute_compliance_report_status(self):
        """Calculate compliance report status."""
        today = fields.Date.today()
        
        for contract in self:
            if not contract.next_report_date:
                contract.compliance_report_status = False
                continue
            
            if contract.next_report_date < today:
                contract.compliance_report_status = 'overdue'
            elif (contract.next_report_date - today).days <= 7:
                contract.compliance_report_status = 'due_soon'
            else:
                contract.compliance_report_status = 'on_time'
    
    def action_view_compliance_tasks(self):
        """Open compliance tasks for this contract."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tâches de Conformité - %s') % self.name,
            'res_model': 'sama.promis.compliance.task',
            'view_mode': 'tree,form,kanban,calendar',
            'domain': [('contract_id', '=', self.id)],
            'context': {
                'default_contract_id': self.id,
                'default_project_id': self.project_id.id,
                'default_responsible_id': self.env.user.id,
            }
        }
    
    def action_generate_compliance_tasks(self):
        """Generate contract-specific compliance tasks from compliance profile."""
        self.ensure_one()
        
        if not self.compliance_profile_id:
            raise ValidationError(_('Aucun profil de conformité défini pour ce contrat.'))
        
        # Get checklist items from profile
        checklist_items = self.compliance_profile_id.get_compliance_checklist_items()
        
        task_obj = self.env['sama.promis.compliance.task']
        created_tasks = task_obj
        
        # Create contract-specific tasks
        for idx, item in enumerate(checklist_items):
            # Only create contract-level tasks (e.g., reports, audits)
            if item.get('level') == 'contract' or item.get('type') in ['report', 'review', 'approval']:
                task_vals = {
                    'name': item.get('name', f'Tâche Contractuelle {idx + 1}'),
                    'description': item.get('description', ''),
                    'project_id': self.project_id.id,
                    'contract_id': self.id,
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
                    'message': _('%d tâches de conformité contractuelles ont été générées.') % len(created_tasks),
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        return True
    
    def action_submit_compliance_report(self):
        """Mark last compliance report date and generate report PDF."""
        self.ensure_one()
        
        self.write({
            'last_compliance_report_date': fields.Date.today()
        })
        
        # Create activity/notification
        self.message_post(
            body=_('Rapport de conformité soumis le %s') % fields.Date.today(),
            message_type='notification'
        )
        
        # Generate the report
        return self.action_generate_compliance_report()
    
    def action_generate_compliance_report(self):
        """Generate donor-specific compliance report using appropriate QWeb template."""
        self.ensure_one()
        
        if not self.compliance_profile_id:
            raise ValidationError(_('Aucun profil de conformité défini.'))
        
        # Determine which report template to use based on compliance profile
        report_action = self.compliance_profile_id.report_template_id
        
        if not report_action:
            # Use default base compliance report
            report_action = self.env.ref('sama_promis.report_sama_promis_compliance_base', raise_if_not_found=False)
        
        if report_action:
            return report_action.report_action(self)
        else:
            raise ValidationError(_('Aucun modèle de rapport configuré pour ce profil de conformité.'))
