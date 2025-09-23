# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Modèle Tag
========================

Système d'étiquetage pour organiser et catégoriser les éléments.
"""

from odoo import models, fields, api


class SamaPromisTag(models.Model):
    """Modèle pour les étiquettes SAMA PROMIS."""
    
    _name = 'sama.promis.tag'
    _description = 'Étiquette SAMA PROMIS'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
        help="Nom de l'étiquette"
    )
    
    color = fields.Integer(
        string='Couleur',
        default=0,
        help="Couleur de l'étiquette (index)"
    )
    
    description = fields.Text(
        string='Description',
        help="Description de l'étiquette"
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        help="Étiquette active ou archivée"
    )
    
    category = fields.Selection([
        ('general', 'Général'),
        ('priority', 'Priorité'),
        ('status', 'Statut'),
        ('type', 'Type'),
        ('location', 'Localisation'),
        ('theme', 'Thématique'),
    ], string='Catégorie', default='general')
    
    # Compteurs d'utilisation
    project_count = fields.Integer(
        string='Nombre de Projets',
        compute='_compute_usage_counts',
        store=True
    )
    
    @api.depends('name')
    def _compute_usage_counts(self):
        """Calcule le nombre d'utilisations."""
        for tag in self:
            tag.project_count = self.env['sama.promis.project'].search_count([
                ('tag_ids', 'in', [tag.id])
            ])
    
    @api.constrains('name')
    def _check_name_unique(self):
        """Vérifie l'unicité du nom."""
        for tag in self:
            if self.search_count([('name', '=', tag.name), ('id', '!=', tag.id)]) > 0:
                raise models.ValidationError(f"Une étiquette avec le nom '{tag.name}' existe déjà.")
    
    def name_get(self):
        """Affichage personnalisé du nom."""
        result = []
        for tag in self:
            name = tag.name
            if tag.category != 'general':
                name = f"[{dict(tag._fields['category'].selection)[tag.category]}] {name}"
            result.append((tag.id, name))
        return result