# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Workflow Mixin
============================

Mixin pour gérer les workflows et cycles de vie des modèles.
Inspiré de SAMA ETAT pour les boutons d'action et transitions.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class WorkflowMixin(models.AbstractModel):
    """
    Mixin pour ajouter des fonctionnalités de workflow à un modèle.
    
    Fournit:
    - Gestion des états avec tracking
    - Boutons d'action standardisés
    - Historique des transitions
    - Validations automatiques
    """
    _name = 'sama.promis.workflow.mixin'
    _description = 'SAMA PROMIS Workflow Mixin'

    # Champs de workflow
    state = fields.Selection(
        selection=[],  # À définir dans les modèles héritants
        string='État',
        default='draft',
        tracking=True,
        help="État actuel de l'enregistrement"
    )
    
    state_history = fields.Text(
        string='Historique des États',
        readonly=True,
        help="Historique des changements d'état"
    )
    
    last_state_change = fields.Datetime(
        string='Dernier Changement d\'État',
        readonly=True,
        help="Date du dernier changement d'état"
    )
    
    state_changed_by = fields.Many2one(
        'res.users',
        string='État Modifié Par',
        readonly=True,
        help="Utilisateur ayant effectué le dernier changement d'état"
    )
    
    # Champs de validation
    can_edit = fields.Boolean(
        string='Peut Modifier',
        compute='_compute_can_edit',
        help="Indique si l'enregistrement peut être modifié"
    )
    
    can_delete = fields.Boolean(
        string='Peut Supprimer',
        compute='_compute_can_delete',
        help="Indique si l'enregistrement peut être supprimé"
    )
    
    workflow_locked = fields.Boolean(
        string='Workflow Verrouillé',
        default=False,
        help="Verrouille le workflow pour empêcher les modifications"
    )

    @api.depends('state', 'workflow_locked')
    def _compute_can_edit(self):
        """Calcule si l'enregistrement peut être modifié."""
        for record in self:
            # États permettant la modification (à personnaliser par modèle)
            editable_states = ['draft', 'submitted', 'under_review']
            record.can_edit = (
                record.state in editable_states and 
                not record.workflow_locked and
                record._check_edit_permissions()
            )

    @api.depends('state', 'workflow_locked')
    def _compute_can_delete(self):
        """Calcule si l'enregistrement peut être supprimé."""
        for record in self:
            # Seuls les brouillons peuvent être supprimés par défaut
            deletable_states = ['draft']
            record.can_delete = (
                record.state in deletable_states and 
                not record.workflow_locked and
                record._check_delete_permissions()
            )

    def _check_edit_permissions(self):
        """Vérifie les permissions de modification (à surcharger)."""
        return True

    def _check_delete_permissions(self):
        """Vérifie les permissions de suppression (à surcharger)."""
        return True

    def _log_state_change(self, old_state, new_state, reason=None):
        """Enregistre un changement d'état dans l'historique."""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        user_name = self.env.user.name
        
        log_entry = f"[{timestamp}] {user_name}: {old_state} → {new_state}"
        if reason:
            log_entry += f" ({reason})"
        
        current_history = self.state_history or ""
        new_history = log_entry + "\n" + current_history
        
        self.write({
            'state_history': new_history,
            'last_state_change': fields.Datetime.now(),
            'state_changed_by': self.env.user.id
        })

    def _validate_state_transition(self, new_state):
        """
        Valide une transition d'état.
        À surcharger dans les modèles pour définir les transitions autorisées.
        """
        return True

    def _before_state_change(self, new_state):
        """Hook appelé avant un changement d'état (à surcharger)."""
        pass

    def _after_state_change(self, old_state, new_state):
        """Hook appelé après un changement d'état (à surcharger)."""
        pass

    def change_state(self, new_state, reason=None):
        """
        Change l'état de l'enregistrement avec validation.
        
        Args:
            new_state (str): Nouvel état
            reason (str): Raison du changement (optionnel)
        """
        self.ensure_one()
        
        if self.workflow_locked:
            raise UserError(_("Le workflow est verrouillé et ne peut pas être modifié."))
        
        old_state = self.state
        
        if old_state == new_state:
            return  # Pas de changement
        
        # Validation de la transition
        if not self._validate_state_transition(new_state):
            raise ValidationError(
                _("Transition non autorisée de '%s' vers '%s'") % (old_state, new_state)
            )
        
        # Hook avant changement
        self._before_state_change(new_state)
        
        # Changement d'état
        self.state = new_state
        
        # Enregistrement dans l'historique
        self._log_state_change(old_state, new_state, reason)
        
        # Hook après changement
        self._after_state_change(old_state, new_state)

    # Boutons d'action standardisés (inspirés de SAMA ETAT)
    
    def action_submit(self):
        """Soumet l'enregistrement pour révision."""
        self.change_state('submitted', 'Soumission pour révision')
        return True

    def action_approve(self):
        """Approuve l'enregistrement."""
        self.change_state('approved', 'Approbation')
        return True

    def action_start(self):
        """Démarre l'exécution."""
        self.change_state('in_progress', 'Démarrage de l\'exécution')
        return True

    def action_suspend(self):
        """Suspend l'exécution."""
        self.change_state('suspended', 'Suspension')
        return True

    def action_resume(self):
        """Reprend l'exécution."""
        self.change_state('in_progress', 'Reprise de l\'exécution')
        return True

    def action_complete(self):
        """Marque comme terminé."""
        self.change_state('completed', 'Finalisation')
        return True

    def action_cancel(self):
        """Annule l'enregistrement."""
        self.change_state('cancelled', 'Annulation')
        return True

    def action_reset_to_draft(self):
        """Remet en brouillon."""
        self.change_state('draft', 'Remise en brouillon')
        return True

    def action_lock_workflow(self):
        """Verrouille le workflow."""
        self.workflow_locked = True
        return True

    def action_unlock_workflow(self):
        """Déverrouille le workflow."""
        self.workflow_locked = False
        return True

    # Méthodes utilitaires

    def get_state_label(self):
        """Retourne le libellé de l'état actuel."""
        state_dict = dict(self._fields['state'].selection)
        return state_dict.get(self.state, self.state)

    def get_available_transitions(self):
        """
        Retourne les transitions disponibles depuis l'état actuel.
        À surcharger dans les modèles pour définir les transitions.
        """
        return []

    def get_state_color(self):
        """Retourne la couleur CSS associée à l'état actuel."""
        colors = {
            'draft': '#6b7280',         # Gris
            'submitted': '#3b82f6',     # Bleu
            'under_review': '#f59e0b',  # Orange
            'approved': '#10b981',      # Vert
            'in_progress': '#3b82f6',   # Bleu
            'suspended': '#f59e0b',     # Orange
            'completed': '#10b981',     # Vert
            'cancelled': '#ef4444',     # Rouge
            'published': '#10b981',     # Vert
            'closed': '#6b7280',        # Gris
            'active': '#10b981',        # Vert
            'expired': '#ef4444',       # Rouge
            'paid': '#10b981',          # Vert
            'rejected': '#ef4444'       # Rouge
        }
        return colors.get(self.state, '#6b7280')

    @api.model
    def get_state_statistics(self):
        """Retourne les statistiques par état."""
        colors = {
            'draft': '#6b7280', 'submitted': '#3b82f6', 'under_review': '#f59e0b',
            'approved': '#10b981', 'in_progress': '#3b82f6', 'suspended': '#f59e0b',
            'completed': '#10b981', 'cancelled': '#ef4444', 'published': '#10b981',
            'closed': '#6b7280', 'active': '#10b981', 'expired': '#ef4444',
            'paid': '#10b981', 'rejected': '#ef4444'
        }
        
        stats = {}
        for state_value, state_label in self._fields['state'].selection:
            count = self.search_count([('state', '=', state_value)])
            stats[state_value] = {
                'label': state_label,
                'count': count,
                'color': colors.get(state_value, '#6b7280')
            }
        return stats