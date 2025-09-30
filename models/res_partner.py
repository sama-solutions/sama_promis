# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Extension Res Partner
===================================

Extension du modèle res.partner pour SAMA PROMIS.
"""

from odoo import models, fields, api
import base64
import io


class ResPartner(models.Model):
    """Extension du modèle res.partner pour SAMA PROMIS."""
    
    _inherit = 'res.partner'

    # Types de partenaires SAMA PROMIS
    is_donor = fields.Boolean(
        string='Bailleur de Fonds',
        help="Ce partenaire est un bailleur de fonds"
    )
    
    is_beneficiary = fields.Boolean(
        string='Bénéficiaire',
        help="Ce partenaire est un bénéficiaire"
    )
    
    is_implementing_partner = fields.Boolean(
        string='Partenaire de Mise en Œuvre',
        help="Ce partenaire participe à la mise en œuvre"
    )
    
    is_government_entity = fields.Boolean(
        string='Entité Gouvernementale',
        help="Ce partenaire est une entité gouvernementale"
    )
    
    is_ngo = fields.Boolean(
        string='ONG',
        help="Ce partenaire est une ONG"
    )
    
    is_private_sector = fields.Boolean(
        string='Secteur Privé',
        help="Ce partenaire appartient au secteur privé"
    )
    
    is_international_org = fields.Boolean(
        string='Organisation Internationale',
        help="Ce partenaire est une organisation internationale"
    )
    
    is_academic = fields.Boolean(
        string='Institution Académique',
        help="Ce partenaire est une institution académique"
    )

    # Type de partenaire (sélection unique)
    partner_type = fields.Selection([
        ('donor', 'Bailleur de Fonds'),
        ('beneficiary', 'Bénéficiaire'),
        ('implementing_partner', 'Partenaire de Mise en Œuvre'),
        ('government_entity', 'Entité Gouvernementale'),
        ('ngo', 'ONG'),
        ('private_sector', 'Secteur Privé'),
        ('international_org', 'Organisation Internationale'),
        ('academic', 'Institution Académique'),
    ], string='Type de Partenaire SAMA PROMIS')

    # Informations spécifiques aux bailleurs
    donor_type = fields.Selection([
        ('bilateral', 'Bilatéral'),
        ('multilateral', 'Multilatéral'),
        ('foundation', 'Fondation'),
        ('private', 'Privé'),
        ('government', 'Gouvernemental'),
    ], string='Type de Bailleur')
    
    funding_capacity = fields.Monetary(
        string='Capacité de Financement',
        currency_field='currency_id',
        help="Capacité de financement annuelle"
    )
    
    preferred_sectors = fields.Many2many(
        'sama.promis.tag',
        'partner_sector_rel',
        'partner_id',
        'tag_id',
        string='Secteurs Préférés',
        domain=[('category', '=', 'theme')]
    )
    
    # Compliance Profiles
    compliance_profile_ids = fields.Many2many(
        'sama.promis.compliance.profile',
        'partner_compliance_profile_rel',
        'partner_id',
        'profile_id',
        string='Profils de Conformité',
        help="Profils de conformité applicables à ce bailleur"
    )
    default_compliance_profile_id = fields.Many2one(
        'sama.promis.compliance.profile',
        string='Profil de Conformité par Défaut',
        help="Profil de conformité utilisé par défaut pour les nouveaux projets"
    )
    
    # Funding origin classification
    funding_origin = fields.Selection([
        ('international', 'International'),
        ('local', 'Local')
    ], string='Origine du Financement', 
       compute='_compute_funding_origin', 
       store=True,
       help="Origine du financement basée sur le pays du partenaire")
    
    funding_origin_manual = fields.Selection([
        ('international', 'International'),
        ('local', 'Local')
    ], string='Origine Manuelle',
       help="Définir manuellement l'origine du financement (remplace le calcul automatique)")
    
    is_international_donor = fields.Boolean(
        string='Bailleur International',
        compute='_compute_funding_origin',
        store=True,
        help="Ce bailleur est international"
    )
    
    is_local_donor = fields.Boolean(
        string='Bailleur Local',
        compute='_compute_funding_origin',
        store=True,
        help="Ce bailleur est local"
    )

    # Informations de contact spécialisées
    focal_point_name = fields.Char(
        string='Point Focal',
        help="Nom du point focal pour SAMA PROMIS"
    )
    
    focal_point_email = fields.Char(
        string='Email Point Focal',
        help="Email du point focal"
    )
    
    focal_point_phone = fields.Char(
        string='Téléphone Point Focal',
        help="Téléphone du point focal"
    )

    # Localisation détaillée
    region = fields.Char(string='Région')
    department = fields.Char(string='Département')
    commune = fields.Char(string='Commune')
    
    # Informations légales et administratives
    registration_number = fields.Char(
        string='Numéro d\'Enregistrement',
        help="Numéro d'enregistrement officiel"
    )
    
    tax_exempt = fields.Boolean(
        string='Exonéré d\'Impôts',
        help="Partenaire exonéré d'impôts"
    )
    
    legal_status = fields.Selection([
        ('association', 'Association'),
        ('foundation', 'Fondation'),
        ('company', 'Société'),
        ('government', 'Gouvernement'),
        ('international', 'Organisation Internationale'),
        ('other', 'Autre'),
    ], string='Statut Légal')

    # Capacités et expertises
    technical_expertise = fields.Text(
        string='Expertise Technique',
        help="Description des expertises techniques"
    )
    
    geographical_coverage = fields.Text(
        string='Couverture Géographique',
        help="Zones géographiques d'intervention"
    )
    
    languages_spoken = fields.Char(
        string='Langues Parlées',
        help="Langues parlées par l'organisation"
    )

    # Évaluation et performance
    performance_rating = fields.Selection([
        ('1', 'Très Faible'),
        ('2', 'Faible'),
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent'),
    ], string='Évaluation Performance')
    
    last_evaluation_date = fields.Date(
        string='Dernière Évaluation',
        help="Date de la dernière évaluation"
    )
    
    evaluation_notes = fields.Text(
        string='Notes d\'Évaluation',
        help="Notes de la dernière évaluation"
    )

    # QR Code pour partenaires
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

    # Statistiques et compteurs
    project_count = fields.Integer(
        string='Nombre de Projets',
        compute='_compute_project_statistics'
    )
    
    total_funding_provided = fields.Monetary(
        string='Financement Total Fourni',
        compute='_compute_project_statistics',
        currency_field='currency_id'
    )
    
    total_international_funding_provided = fields.Monetary(
        string='Financement International Fourni',
        compute='_compute_project_statistics',
        currency_field='currency_id',
        help="Total des financements internationaux fournis"
    )
    
    total_local_funding_provided = fields.Monetary(
        string='Financement Local Fourni',
        compute='_compute_project_statistics',
        currency_field='currency_id',
        help="Total des financements locaux fournis"
    )
    
    active_projects_count = fields.Integer(
        string='Projets Actifs',
        compute='_compute_project_statistics'
    )

    @api.depends('country_id', 'funding_origin_manual', 'is_donor')
    def _compute_funding_origin(self):
        """Compute funding origin based on partner's country vs company country."""
        company_country = self.env.company.country_id
        
        for partner in self:
            # Use manual override if set
            if partner.funding_origin_manual:
                partner.funding_origin = partner.funding_origin_manual
            elif partner.is_donor and partner.country_id:
                # Compare partner country with company country
                if partner.country_id != company_country:
                    partner.funding_origin = 'international'
                else:
                    partner.funding_origin = 'local'
            else:
                # Default to local if no country specified
                partner.funding_origin = 'local'
            
            # Set boolean flags
            partner.is_international_donor = (partner.funding_origin == 'international')
            partner.is_local_donor = (partner.funding_origin == 'local')
    
    @api.depends('name', 'id')
    def _compute_qr_code_data(self):
        """Calcule les données du QR code."""
        # TODO: Pointer vers le portail public une fois développé
        # Pour l'instant, on pointe vers le backend Odoo
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://sama-promis.sn')
        for partner in self:
            if partner.id:
                # Format backend: /web#id={id}&model={model}&view_type=form
                partner.qr_code_data = f"{base_url}/web#id={partner.id}&model=res.partner&view_type=form"
            else:
                partner.qr_code_data = False

    @api.depends('qr_code_data')
    def _compute_qr_code_image(self):
        """Génère l'image du QR code."""
        try:
            import qrcode
            
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
            for partner in self:
                partner.qr_code_image = False

    def _compute_project_statistics(self):
        """Calcule les statistiques des projets."""
        for partner in self:
            # Projets où le partenaire est impliqué
            projects_as_main = self.env['sama.promis.project'].search([
                ('partner_id', '=', partner.id)
            ])
            projects_as_donor = self.env['sama.promis.project'].search([
                ('donor_id', '=', partner.id)
            ])
            projects_as_implementer = self.env['sama.promis.project'].search([
                ('implementing_partner_ids', 'in', [partner.id])
            ])
            
            all_projects = projects_as_main | projects_as_donor | projects_as_implementer
            
            partner.project_count = len(all_projects)
            partner.active_projects_count = len(all_projects.filtered(
                lambda p: p.state in ['approved', 'in_progress']
            ))
            
            # Calcul du financement total fourni (si bailleur)
            if partner.is_donor:
                # Legacy calculation from donor_contribution
                partner.total_funding_provided = sum(projects_as_donor.mapped('donor_contribution'))
                
                # Calculate from funding sources
                funding_sources = self.env['sama.promis.project.funding.source'].search([
                    ('partner_id', '=', partner.id)
                ])
                
                international_total = 0.0
                local_total = 0.0
                
                for source in funding_sources:
                    # Convert to partner currency if needed
                    amount = source.amount
                    if source.currency_id != partner.currency_id:
                        amount = source.currency_id._convert(
                            amount,
                            partner.currency_id,
                            self.env.company,
                            fields.Date.today()
                        )
                    
                    if source.funding_origin == 'international':
                        international_total += amount
                    elif source.funding_origin == 'local':
                        local_total += amount
                
                partner.total_international_funding_provided = international_total
                partner.total_local_funding_provided = local_total
            else:
                partner.total_funding_provided = 0
                partner.total_international_funding_provided = 0
                partner.total_local_funding_provided = 0

    @api.constrains('default_compliance_profile_id', 'compliance_profile_ids')
    def _check_default_compliance_profile(self):
        """Ensure default compliance profile is in the list of profiles."""
        for partner in self:
            if partner.default_compliance_profile_id:
                if partner.default_compliance_profile_id not in partner.compliance_profile_ids:
                    raise ValidationError(_(
                        'Le profil de conformité par défaut doit être dans la liste des profils de conformité.'
                    ))
    
    @api.onchange('is_donor')
    def _onchange_is_donor(self):
        """Actions lors du changement du statut bailleur."""
        if self.is_donor:
            self.partner_type = 'donor'
            self.is_company = True

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """Actions lors du changement du type de partenaire."""
        # Réinitialiser tous les booléens
        self.is_donor = False
        self.is_beneficiary = False
        self.is_implementing_partner = False
        self.is_government_entity = False
        self.is_ngo = False
        self.is_private_sector = False
        self.is_international_org = False
        self.is_academic = False
        
        # Activer le bon booléen selon le type
        if self.partner_type == 'donor':
            self.is_donor = True
        elif self.partner_type == 'beneficiary':
            self.is_beneficiary = True
        elif self.partner_type == 'implementing_partner':
            self.is_implementing_partner = True
        elif self.partner_type == 'government_entity':
            self.is_government_entity = True
        elif self.partner_type == 'ngo':
            self.is_ngo = True
        elif self.partner_type == 'private_sector':
            self.is_private_sector = True
        elif self.partner_type == 'international_org':
            self.is_international_org = True
        elif self.partner_type == 'academic':
            self.is_academic = True

    def action_view_projects(self):
        """Voir les projets du partenaire."""
        domain = [
            '|', '|',
            ('partner_id', '=', self.id),
            ('donor_id', '=', self.id),
            ('implementing_partner_ids', 'in', [self.id])
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projets de {self.name}',
            'res_model': 'sama.promis.project',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'default_partner_id': self.id}
        }