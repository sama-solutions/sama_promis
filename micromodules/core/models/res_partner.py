# -*- coding: utf-8 -*-
"""
SAMA PROMIS Core - Partner Extension
====================================

Extension du modèle res.partner pour SAMA PROMIS.
Ajoute les fonctionnalités spécifiques aux bailleurs et bénéficiaires.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """Extension du modèle Partner pour SAMA PROMIS."""
    _inherit = 'res.partner'

    # Types de partenaires SAMA PROMIS
    partner_type = fields.Selection(
        selection=[
            ('donor', 'Bailleur de Fonds'),
            ('beneficiary', 'Bénéficiaire'),
            ('implementing_partner', 'Partenaire de Mise en Œuvre'),
            ('government', 'Gouvernement'),
            ('ngo', 'ONG'),
            ('private_sector', 'Secteur Privé'),
            ('academic', 'Académique'),
            ('citizen', 'Citoyen')
        ],
        string='Type de Partenaire',
        help="Type de partenaire dans le système SAMA PROMIS"
    )
    
    # Champs spécifiques aux bailleurs
    is_donor = fields.Boolean(
        string='Est un Bailleur',
        help="Indique si ce partenaire est un bailleur de fonds"
    )
    
    donor_type = fields.Selection(
        selection=[
            ('multilateral', 'Multilatéral'),
            ('bilateral', 'Bilatéral'),
            ('foundation', 'Fondation'),
            ('private', 'Privé'),
            ('government', 'Gouvernemental')
        ],
        string='Type de Bailleur',
        help="Type de bailleur de fonds"
    )
    
    donor_code = fields.Char(
        string='Code Bailleur',
        help="Code unique du bailleur"
    )
    
    funding_areas = fields.Text(
        string='Domaines de Financement',
        help="Domaines d'intervention du bailleur"
    )
    
    # Champs spécifiques aux bénéficiaires
    is_beneficiary = fields.Boolean(
        string='Est un Bénéficiaire',
        help="Indique si ce partenaire est un bénéficiaire"
    )
    
    beneficiary_type = fields.Selection(
        selection=[
            ('ngo', 'ONG'),
            ('association', 'Association'),
            ('cooperative', 'Coopérative'),
            ('company', 'Entreprise'),
            ('institution', 'Institution'),
            ('individual', 'Individuel')
        ],
        string='Type de Bénéficiaire',
        help="Type de bénéficiaire"
    )
    
    registration_number = fields.Char(
        string='Numéro d\'Enregistrement',
        help="Numéro d'enregistrement officiel"
    )
    
    legal_status = fields.Char(
        string='Statut Juridique',
        help="Statut juridique de l'organisation"
    )
    
    # Informations bancaires
    bank_name = fields.Char(
        string='Nom de la Banque',
        help="Nom de la banque"
    )
    
    bank_account_number = fields.Char(
        string='Numéro de Compte',
        help="Numéro de compte bancaire"
    )
    
    swift_code = fields.Char(
        string='Code SWIFT',
        help="Code SWIFT de la banque"
    )
    
    # Capacités et certifications
    technical_capacity = fields.Text(
        string='Capacités Techniques',
        help="Description des capacités techniques"
    )
    
    certifications = fields.Text(
        string='Certifications',
        help="Certifications et accréditations"
    )
    
    experience_years = fields.Integer(
        string='Années d\'Expérience',
        help="Nombre d'années d'expérience"
    )
    
    # Évaluation et notation
    performance_rating = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Bon'),
            ('average', 'Moyen'),
            ('poor', 'Faible'),
            ('not_rated', 'Non Évalué')
        ],
        string='Évaluation Performance',
        default='not_rated',
        help="Évaluation de la performance"
    )
    
    risk_level = fields.Selection(
        selection=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
            ('critical', 'Critique')
        ],
        string='Niveau de Risque',
        default='low',
        help="Niveau de risque associé"
    )
    
    # Relations avec les projets
    project_ids = fields.One2many(
        'sama.promis.project',
        'partner_id',
        string='Projets',
        help="Projets associés à ce partenaire"
    )
    
    donor_project_ids = fields.One2many(
        'sama.promis.project',
        'donor_id',
        string='Projets Financés',
        help="Projets financés par ce bailleur"
    )
    
    # Statistiques
    total_projects = fields.Integer(
        string='Total Projets',
        compute='_compute_project_statistics',
        help="Nombre total de projets"
    )
    
    active_projects = fields.Integer(
        string='Projets Actifs',
        compute='_compute_project_statistics',
        help="Nombre de projets actifs"
    )
    
    total_funding = fields.Monetary(
        string='Financement Total',
        compute='_compute_funding_statistics',
        help="Montant total des financements"
    )
    
    # QR Code spécifique
    qr_code_data = fields.Char(
        string='Données QR Code',
        compute='_compute_qr_code_data',
        store=True,
        help="Données encodées dans le QR code"
    )
    
    qr_code_image = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code_image',
        store=True,
        help="Image du QR code"
    )

    @api.depends('project_ids', 'donor_project_ids')
    def _compute_project_statistics(self):
        """Calcule les statistiques des projets."""
        for partner in self:
            all_projects = partner.project_ids + partner.donor_project_ids
            partner.total_projects = len(all_projects)
            partner.active_projects = len(all_projects.filtered(lambda p: p.state == 'in_progress'))

    @api.depends('donor_project_ids')
    def _compute_funding_statistics(self):
        """Calcule les statistiques de financement."""
        for partner in self:
            if partner.is_donor and partner.donor_project_ids:
                partner.total_funding = sum(partner.donor_project_ids.mapped('total_budget'))
            else:
                partner.total_funding = 0

    @api.depends('name', 'id', 'partner_type')
    def _compute_qr_code_data(self):
        """Calcule les données du QR code pour le partenaire."""
        for partner in self:
            if partner.id:
                base_url = partner.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://sama-promis.sn')
                partner.qr_code_data = f"{base_url}/promispublic/partner/{partner.id}"
            else:
                partner.qr_code_data = False

    @api.depends('qr_code_data')
    def _compute_qr_code_image(self):
        """Génère l'image du QR code."""
        try:
            import qrcode
            import io
            import base64
            
            for partner in self:
                if partner.qr_code_data:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(partner.qr_code_data)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    
                    partner.qr_code_image = base64.b64encode(buffer.getvalue()).decode()
                else:
                    partner.qr_code_image = False
        except ImportError:
            # Si qrcode n'est pas installé, on ignore
            for partner in self:
                partner.qr_code_image = False

    @api.onchange('is_donor')
    def _onchange_is_donor(self):
        """Met à jour le type de partenaire quand is_donor change."""
        if self.is_donor:
            self.partner_type = 'donor'
            self.is_beneficiary = False

    @api.onchange('is_beneficiary')
    def _onchange_is_beneficiary(self):
        """Met à jour le type de partenaire quand is_beneficiary change."""
        if self.is_beneficiary:
            self.partner_type = 'beneficiary'
            self.is_donor = False

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """Met à jour les flags selon le type de partenaire."""
        if self.partner_type == 'donor':
            self.is_donor = True
            self.is_beneficiary = False
        elif self.partner_type == 'beneficiary':
            self.is_beneficiary = True
            self.is_donor = False
        else:
            self.is_donor = False
            self.is_beneficiary = False

    @api.constrains('donor_code')
    def _check_donor_code_unique(self):
        """Vérifie l'unicité du code bailleur."""
        for partner in self:
            if partner.donor_code and partner.is_donor:
                existing = self.search([
                    ('donor_code', '=', partner.donor_code),
                    ('is_donor', '=', True),
                    ('id', '!=', partner.id)
                ])
                if existing:
                    raise ValidationError(_("Le code bailleur '%s' existe déjà.") % partner.donor_code)

    @api.constrains('registration_number')
    def _check_registration_number_unique(self):
        """Vérifie l'unicité du numéro d'enregistrement."""
        for partner in self:
            if partner.registration_number and partner.is_beneficiary:
                existing = self.search([
                    ('registration_number', '=', partner.registration_number),
                    ('is_beneficiary', '=', True),
                    ('id', '!=', partner.id)
                ])
                if existing:
                    raise ValidationError(_("Le numéro d'enregistrement '%s' existe déjà.") % partner.registration_number)

    def action_view_projects(self):
        """Affiche les projets associés au partenaire."""
        self.ensure_one()
        
        if self.is_donor:
            projects = self.donor_project_ids
            title = f"Projets Financés par {self.name}"
        else:
            projects = self.project_ids
            title = f"Projets de {self.name}"
        
        return {
            'type': 'ir.actions.act_window',
            'name': title,
            'res_model': 'sama.promis.project',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', projects.ids)],
            'context': {'default_partner_id': self.id if not self.is_donor else False,
                       'default_donor_id': self.id if self.is_donor else False}
        }

    def get_performance_color(self):
        """Retourne la couleur associée à l'évaluation de performance."""
        colors = {
            'excellent': '#10b981',    # Vert
            'good': '#3b82f6',         # Bleu
            'average': '#f59e0b',      # Orange
            'poor': '#ef4444',         # Rouge
            'not_rated': '#6b7280'     # Gris
        }
        return colors.get(self.performance_rating, '#6b7280')

    def get_risk_color(self):
        """Retourne la couleur associée au niveau de risque."""
        colors = {
            'low': '#10b981',      # Vert
            'medium': '#f59e0b',   # Orange
            'high': '#ef4444',     # Rouge
            'critical': '#7c2d12'  # Rouge foncé
        }
        return colors.get(self.risk_level, '#6b7280')

    @api.model
    def get_partner_statistics(self):
        """Retourne les statistiques globales des partenaires."""
        total_partners = self.search_count([])
        donors = self.search_count([('is_donor', '=', True)])
        beneficiaries = self.search_count([('is_beneficiary', '=', True)])
        
        return {
            'total_partners': total_partners,
            'donors': donors,
            'beneficiaries': beneficiaries,
            'others': total_partners - donors - beneficiaries
        }