# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Audit Mixin
=========================

Mixin pour ajouter des fonctionnalités d'audit et de traçabilité.
"""

from odoo import models, fields, api
from datetime import datetime


class AuditMixin(models.AbstractModel):
    """
    Mixin pour ajouter des fonctionnalités d'audit à un modèle.
    
    Fournit:
    - Traçabilité des créations/modifications
    - Historique des actions
    - Logs d'audit
    - Métadonnées de suivi
    """
    _name = 'sama.promis.audit.mixin'
    _description = 'SAMA PROMIS Audit Mixin'

    # Champs d'audit automatiques
    created_by = fields.Many2one(
        'res.users',
        string='Créé Par',
        readonly=True,
        default=lambda self: self.env.user,
        help="Utilisateur ayant créé l'enregistrement"
    )
    
    created_date = fields.Datetime(
        string='Date de Création',
        readonly=True,
        default=fields.Datetime.now,
        help="Date et heure de création"
    )
    
    last_modified_by = fields.Many2one(
        'res.users',
        string='Dernière Modification Par',
        readonly=True,
        help="Utilisateur ayant effectué la dernière modification"
    )
    
    last_modified_date = fields.Datetime(
        string='Date de Dernière Modification',
        readonly=True,
        help="Date et heure de la dernière modification"
    )
    
    # Champs d'audit avancés
    audit_log = fields.Text(
        string='Journal d\'Audit',
        readonly=True,
        help="Journal détaillé des actions effectuées"
    )
    
    access_count = fields.Integer(
        string='Nombre d\'Accès',
        default=0,
        readonly=True,
        help="Nombre de fois que l'enregistrement a été consulté"
    )
    
    last_access_date = fields.Datetime(
        string='Dernier Accès',
        readonly=True,
        help="Date du dernier accès à l'enregistrement"
    )
    
    last_access_by = fields.Many2one(
        'res.users',
        string='Dernier Accès Par',
        readonly=True,
        help="Utilisateur ayant effectué le dernier accès"
    )
    
    # Métadonnées
    version = fields.Integer(
        string='Version',
        default=1,
        readonly=True,
        help="Numéro de version de l'enregistrement"
    )
    
    is_archived = fields.Boolean(
        string='Archivé',
        default=False,
        help="Indique si l'enregistrement est archivé"
    )
    
    archive_date = fields.Datetime(
        string='Date d\'Archivage',
        readonly=True,
        help="Date d'archivage de l'enregistrement"
    )
    
    archive_reason = fields.Text(
        string='Raison d\'Archivage',
        help="Raison de l'archivage"
    )

    @api.model
    def create(self, vals):
        """Surcharge create pour ajouter l'audit."""
        record = super().create(vals)
        record._log_audit_action('create', 'Création de l\'enregistrement')
        return record

    def write(self, vals):
        """Surcharge write pour ajouter l'audit."""
        # Enregistrer les valeurs avant modification pour comparaison
        old_values = {}
        for record in self:
            old_values[record.id] = {
                field: record[field] for field in vals.keys() 
                if field in record._fields
            }
        
        # Mise à jour des champs d'audit
        vals.update({
            'last_modified_by': self.env.user.id,
            'last_modified_date': fields.Datetime.now(),
            'version': self.version + 1 if 'version' in self._fields else 1
        })
        
        result = super().write(vals)
        
        # Log des modifications
        for record in self:
            changes = []
            old_vals = old_values.get(record.id, {})
            for field, new_value in vals.items():
                if field in old_vals:
                    old_value = old_vals[field]
                    if old_value != new_value:
                        field_label = record._fields[field].string if field in record._fields else field
                        changes.append(f"{field_label}: {old_value} → {new_value}")
            
            if changes:
                change_summary = "; ".join(changes)
                record._log_audit_action('update', f'Modification: {change_summary}')
        
        return result

    def unlink(self):
        """Surcharge unlink pour ajouter l'audit."""
        for record in self:
            record._log_audit_action('delete', 'Suppression de l\'enregistrement')
        return super().unlink()

    def read(self, fields=None, load='_classic_read'):
        """Surcharge read pour tracker les accès."""
        result = super().read(fields, load)
        
        # Mise à jour des statistiques d'accès (en mode silencieux)
        try:
            self.sudo().write({
                'access_count': self.access_count + 1,
                'last_access_date': fields.Datetime.now(),
                'last_access_by': self.env.user.id
            })
        except:
            # En cas d'erreur, on continue sans bloquer
            pass
        
        return result

    def _log_audit_action(self, action_type, description):
        """
        Enregistre une action dans le journal d'audit.
        
        Args:
            action_type (str): Type d'action (create, update, delete, etc.)
            description (str): Description de l'action
        """
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        user_name = self.env.user.name
        user_ip = self.env.context.get('user_ip', 'Unknown')
        
        log_entry = f"[{timestamp}] {action_type.upper()} par {user_name} (IP: {user_ip}): {description}"
        
        current_log = self.audit_log or ""
        new_log = log_entry + "\n" + current_log
        
        # Limiter la taille du log (garder les 1000 derniers caractères)
        if len(new_log) > 10000:
            new_log = new_log[:10000] + "\n... (log tronqué)"
        
        # Mise à jour silencieuse pour éviter les boucles
        self.sudo().write({'audit_log': new_log})

    def action_archive(self, reason=None):
        """Archive l'enregistrement."""
        self.write({
            'is_archived': True,
            'archive_date': fields.Datetime.now(),
            'archive_reason': reason or 'Archivage manuel'
        })
        self._log_audit_action('archive', f'Archivage: {reason or "Manuel"}')

    def action_unarchive(self):
        """Désarchive l'enregistrement."""
        self.write({
            'is_archived': False,
            'archive_date': False,
            'archive_reason': False
        })
        self._log_audit_action('unarchive', 'Désarchivage')

    def get_audit_summary(self):
        """Retourne un résumé de l'audit."""
        self.ensure_one()
        return {
            'created_by': self.created_by.name if self.created_by else 'Inconnu',
            'created_date': self.created_date,
            'last_modified_by': self.last_modified_by.name if self.last_modified_by else 'Aucune',
            'last_modified_date': self.last_modified_date,
            'version': self.version,
            'access_count': self.access_count,
            'last_access_date': self.last_access_date,
            'last_access_by': self.last_access_by.name if self.last_access_by else 'Aucun',
            'is_archived': self.is_archived
        }

    @api.model
    def get_audit_statistics(self):
        """Retourne les statistiques d'audit globales."""
        total_records = self.search_count([])
        archived_records = self.search_count([('is_archived', '=', True)])
        active_records = total_records - archived_records
        
        # Statistiques par utilisateur
        user_stats = {}
        for record in self.search([]):
            user = record.created_by.name if record.created_by else 'Inconnu'
            if user not in user_stats:
                user_stats[user] = 0
            user_stats[user] += 1
        
        return {
            'total_records': total_records,
            'active_records': active_records,
            'archived_records': archived_records,
            'user_statistics': user_stats
        }