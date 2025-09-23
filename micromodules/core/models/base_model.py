# -*- coding: utf-8 -*-
"""
SAMA PROMIS Core - Base Model
=============================

Modèle de base pour tous les modèles SAMA PROMIS.
Inclut QR codes, workflows, audit et fonctionnalités communes.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid


class SamaPromisBaseModel(models.AbstractModel):
    """
    Modèle de base abstrait pour tous les modèles SAMA PROMIS.
    
    Fournit:
    - QR codes automatiques
    - Référence unique
    - Intégration avec les mixins workflow et audit
    - Fonctionnalités communes
    """
    _name = 'sama.promis.base.model'
    _description = 'SAMA PROMIS Base Model'
    _inherit = ['sama.promis.workflow.mixin', 'sama.promis.audit.mixin']
    _order = 'create_date desc'

    # Champs de base
    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
        help="Nom de l'enregistrement"
    )
    
    reference = fields.Char(
        string='Référence',
        readonly=True,
        copy=False,
        help="Référence unique de l'enregistrement"
    )
    
    description = fields.Text(
        string='Description',
        help="Description détaillée"
    )
    
    notes = fields.Text(
        string='Notes',
        help="Notes internes"
    )
    
    # Champs QR Code
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
    
    qr_code_url = fields.Char(
        string='URL QR Code',
        compute='_compute_qr_code_url',
        help="URL publique de l'enregistrement"
    )
    
    # Champs de priorité et tags
    priority = fields.Selection(
        selection=[
            ('low', 'Faible'),
            ('medium', 'Moyenne'),
            ('high', 'Élevée'),
            ('urgent', 'Urgente')
        ],
        string='Priorité',
        default='medium',
        tracking=True,
        help="Niveau de priorité"
    )
    
    tag_ids = fields.Many2many(
        'sama.promis.tag',
        string='Étiquettes',
        help="Étiquettes pour catégoriser l'enregistrement"
    )
    
    # Champs de dates
    start_date = fields.Date(
        string='Date de Début',
        help="Date de début prévue"
    )
    
    end_date = fields.Date(
        string='Date de Fin',
        help="Date de fin prévue"
    )
    
    deadline = fields.Date(
        string='Échéance',
        tracking=True,
        help="Date limite"
    )
    
    # Champs calculés
    duration_days = fields.Integer(
        string='Durée (jours)',
        compute='_compute_duration',
        store=True,
        help="Durée en jours entre début et fin"
    )
    
    is_overdue = fields.Boolean(
        string='En Retard',
        compute='_compute_is_overdue',
        help="Indique si l'échéance est dépassée"
    )
    
    days_to_deadline = fields.Integer(
        string='Jours jusqu\'à l\'échéance',
        compute='_compute_days_to_deadline',
        help="Nombre de jours jusqu'à l'échéance"
    )

    @api.model
    def create(self, vals):
        """Génère automatiquement la référence à la création."""
        if not vals.get('reference'):
            vals['reference'] = self._generate_reference()
        return super().create(vals)

    def _generate_reference(self):
        """Génère une référence unique pour l'enregistrement."""
        import uuid
        from datetime import datetime
        
        # Préfixe basé sur le modèle
        model_prefix = self._get_reference_prefix()
        timestamp = datetime.now().strftime('%Y%m%d')
        random_part = str(uuid.uuid4().int)[:8]
        return f"{model_prefix}-{timestamp}-{random_part}"

    def _get_reference_prefix(self):
        """Retourne le préfixe de référence pour le modèle (à surcharger)."""
        return 'SP'  # SAMA PROMIS par défaut

    @api.depends('name', 'reference', 'id')
    def _compute_qr_code_data(self):
        """Calcule les données à encoder dans le QR code."""
        for record in self:
            if record.id:
                # URL publique vers l'enregistrement
                base_url = record.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://sama-promis.sn')
                record.qr_code_data = f"{base_url}/promispublic/{record._name.replace('.', '_')}/{record.id}"
            else:
                record.qr_code_data = False

    @api.depends('qr_code_data')
    def _compute_qr_code_image(self):
        """Génère l'image du QR code."""
        try:
            import qrcode
            import io
            import base64
            
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
            # Si qrcode n'est pas installé, on ignore
            for record in self:
                record.qr_code_image = False

    @api.depends('qr_code_data')
    def _compute_qr_code_url(self):
        """Calcule l'URL publique de l'enregistrement."""
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

    @api.depends('deadline')
    def _compute_is_overdue(self):
        """Vérifie si l'échéance est dépassée."""
        today = fields.Date.today()
        for record in self:
            record.is_overdue = record.deadline and record.deadline < today

    @api.depends('deadline')
    def _compute_days_to_deadline(self):
        """Calcule le nombre de jours jusqu'à l'échéance."""
        today = fields.Date.today()
        for record in self:
            if record.deadline:
                delta = record.deadline - today
                record.days_to_deadline = delta.days
            else:
                record.days_to_deadline = 0

    def name_get(self):
        """Personnalise l'affichage du nom avec la référence."""
        result = []
        for record in self:
            if record.reference:
                name = f"[{record.reference}] {record.name}"
            else:
                name = record.name
            result.append((record.id, name))
        return result


class SamaPromisTag(models.Model):
    """Modèle pour les étiquettes SAMA PROMIS."""
    _name = 'sama.promis.tag'
    _description = 'SAMA PROMIS Tag'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
        help="Nom de l'étiquette"
    )
    
    color = fields.Integer(
        string='Couleur',
        default=0,
        help="Couleur de l'étiquette"
    )
    
    description = fields.Text(
        string='Description',
        help="Description de l'étiquette"
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        help="Étiquette active"
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Le nom de l\'étiquette doit être unique.')
    ]