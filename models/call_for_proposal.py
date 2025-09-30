# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class SamaPromisCallProposal(models.Model):
    _name = 'sama.promis.call.proposal'
    _description = 'Appel à Propositions SAMA PROMIS'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Référence", required=True, tracking=True)
    title = fields.Char(string="Titre de l'Appel", required=True, tracking=True)
    description = fields.Html(string="Description")

    # Dates
    publication_date = fields.Date(string="Date de Publication",
                                 default=fields.Date.today, tracking=True)
    submission_deadline = fields.Date(string="Date Limite de Soumission",
                                    required=True, tracking=True)
    evaluation_start_date = fields.Date(string="Début de l'Évaluation")
    evaluation_end_date = fields.Date(string="Fin de l'Évaluation")

    # Financial Information
    total_budget = fields.Monetary(string="Budget Total",
                                 currency_field='currency_id', tracking=True)
    min_grant_amount = fields.Monetary(string="Subvention Minimale",
                                     currency_field='currency_id')
    max_grant_amount = fields.Monetary(string="Subvention Maximale",
                                     currency_field='currency_id')
    currency_id = fields.Many2one('res.currency',
                                default=lambda self: self.env.company.currency_id)

    # Status
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('evaluation', 'En Évaluation'),
        ('closed', 'Clôturé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', tracking=True)

    # Relations
    donor_id = fields.Many2one('res.partner', string="Bailleur de Fonds",
                             domain="[('is_company', '=', True)]", required=True)
    project_ids = fields.One2many('sama.promis.project', 'call_for_proposal_id',
                                string="Projets Soumis")
    evaluation_criteria_ids = fields.One2many('sama.promis.evaluation.criteria',
                                           'call_id',
                                           string="Critères d'Évaluation")

    # Documents
    guideline_document = fields.Binary(string="Document de Lignes Directrices")
    guideline_filename = fields.Char(string="Nom du Fichier des Lignes Directrices")
    template_document = fields.Binary(string="Modèle de Proposition")
    template_filename = fields.Char(string="Nom du Fichier du Modèle")

    # Statistics
    submission_count = fields.Integer(string="Nombre de Soumissions",
                                    compute='_compute_submission_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code('sama.promis.call.proposal') or _('New')
        return super().create(vals_list)

    @api.depends('project_ids')
    def _compute_submission_count(self):
        for call in self:
            call.submission_count = len(call.project_ids)

    @api.constrains('submission_deadline', 'publication_date')
    def _check_dates(self):
        for call in self:
            if call.submission_deadline and call.publication_date:
                if call.submission_deadline <= call.publication_date:
                    raise ValidationError(
                        _("La date limite de soumission doit être postérieure à la date de publication.")
                    )

    def action_publish(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("Seuls les appels en brouillon peuvent être publiés."))
        self.write({'state': 'published'})

    def action_start_evaluation(self):
        self.ensure_one()
        if self.state != 'published':
            raise ValidationError(_("Seuls les appels publiés peuvent passer en évaluation."))
        self.write({
            'state': 'evaluation',
            'evaluation_start_date': fields.Date.today(),
        })

    def action_close(self):
        self.ensure_one()
        if self.state != 'evaluation':
            raise ValidationError(_("Seuls les appels en évaluation peuvent être clôturés."))
        self.write({
            'state': 'closed',
            'evaluation_end_date': fields.Date.today(),
        })

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})


class SamaPromisEvaluationCriteria(models.Model):
    _name = 'sama.promis.evaluation.criteria'
    _description = "Critères d'Évaluation des Propositions"
    _order = 'sequence, id'

    name = fields.Char(string="Critère", required=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer(string="Séquence", default=10)
    weight = fields.Float(string="Poids (%)",
                         help="Poids en pourcentage pour le calcul du score total")
    call_id = fields.Many2one('sama.promis.call.proposal',
                            string="Appel à Propositions",
                            ondelete='cascade')

    _sql_constraints = [
        ('weight_range', 'CHECK(weight > 0 AND weight <= 100)',
         "Le poids doit être compris entre 0 et 100%.")
    ]
