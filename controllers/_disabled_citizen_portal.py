# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Page Citoyenne "SAMA PROMIS ET MOI"
=================================================

Contrôleur pour la page citoyenne personnalisée.
Affiche toute l'activité liée à l'utilisateur dans un style moderne.
"""

from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
import json


class CitizenPortalController(http.Controller):
    """Contrôleur pour la page citoyenne SAMA PROMIS ET MOI."""

    @http.route(['/promispublic/citizen'], type='http', auth="public", website=True)
    def citizen_portal(self, **kw):
        """
        Page principale "SAMA PROMIS ET MOI".
        
        Affiche:
        - Activité personnalisée de l'utilisateur
        - Projets suivis
        - Notifications
        - Historique des interactions
        """
        # Vérifier si l'utilisateur est connecté
        if request.env.user._is_public():
            # Utilisateur non connecté - affichage générique
            return self._render_public_citizen_view(**kw)
        else:
            # Utilisateur connecté - affichage personnalisé
            return self._render_authenticated_citizen_view(**kw)

    def _render_public_citizen_view(self, **kw):
        """Affichage pour les utilisateurs non connectés."""
        Project = request.env['sama.promis.project'].sudo()
        
        # Projets récents et populaires
        recent_projects = Project.search([
            ('state', 'in', ['approved', 'in_progress', 'completed']),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=30))
        ], limit=6, order='create_date desc')
        
        popular_projects = Project.search([
            ('state', 'in', ['approved', 'in_progress', 'completed']),
            ('priority', 'in', ['high', 'urgent'])
        ], limit=6, order='total_budget desc')
        
        # Statistiques générales
        total_projects = Project.search_count([('state', 'in', ['approved', 'in_progress', 'completed'])])
        total_budget = sum(Project.search([('state', 'in', ['approved', 'in_progress', 'completed'])]).mapped('total_budget'))
        
        # Projets par région (pour engagement citoyen)
        regions_data = {}
        all_projects = Project.search([('state', 'in', ['approved', 'in_progress', 'completed'])])
        for project in all_projects:
            if project.region:
                if project.region not in regions_data:
                    regions_data[project.region] = {
                        'count': 0,
                        'budget': 0,
                        'projects': []
                    }
                regions_data[project.region]['count'] += 1
                regions_data[project.region]['budget'] += project.total_budget or 0
                regions_data[project.region]['projects'].append(project)
        
        values = {
            'is_authenticated': False,
            'recent_projects': recent_projects,
            'popular_projects': popular_projects,
            'total_projects': total_projects,
            'total_budget': total_budget,
            'regions_data': regions_data,
            'company_name': request.env.company.name or "SAMA ETAT",
            'page_title': 'SAMA PROMIS ET MOI',
        }
        
        return request.render('sama_promis.citizen_portal_public', values)

    def _render_authenticated_citizen_view(self, **kw):
        """Affichage pour les utilisateurs connectés."""
        user = request.env.user
        Project = request.env['sama.promis.project'].sudo()
        
        # Projets liés à l'utilisateur (via partenaire)
        user_projects = []
        if user.partner_id:
            # Projets où l'utilisateur est partenaire principal
            user_projects.extend(Project.search([
                ('partner_id', '=', user.partner_id.id),
                ('state', 'in', ['approved', 'in_progress', 'completed'])
            ]))
            
            # Projets où l'utilisateur est partenaire de mise en œuvre
            user_projects.extend(Project.search([
                ('implementing_partner_ids', 'in', [user.partner_id.id]),
                ('state', 'in', ['approved', 'in_progress', 'completed'])
            ]))
        
        # Supprimer les doublons
        user_projects = list(set(user_projects))
        
        # Projets suivis (simulation - à implémenter avec un modèle de suivi)
        followed_projects = Project.search([
            ('state', 'in', ['approved', 'in_progress', 'completed'])
        ], limit=5, order='create_date desc')
        
        # Activité récente de l'utilisateur
        recent_activity = self._get_user_recent_activity(user)
        
        # Notifications pour l'utilisateur
        notifications = self._get_user_notifications(user)
        
        # Statistiques personnalisées
        user_stats = {
            'my_projects': len(user_projects),
            'followed_projects': len(followed_projects),
            'total_budget_involved': sum(p.total_budget for p in user_projects),
            'active_projects': len([p for p in user_projects if p.state == 'in_progress']),
        }
        
        # Projets recommandés (basés sur l'activité de l'utilisateur)
        recommended_projects = self._get_recommended_projects(user, user_projects)
        
        values = {
            'is_authenticated': True,
            'user': user,
            'user_projects': user_projects,
            'followed_projects': followed_projects,
            'recent_activity': recent_activity,
            'notifications': notifications,
            'user_stats': user_stats,
            'recommended_projects': recommended_projects,
            'company_name': request.env.company.name or "SAMA ETAT",
            'page_title': f'SAMA PROMIS ET MOI - {user.name}',
        }
        
        return request.render('sama_promis.citizen_portal_authenticated', values)

    def _get_user_recent_activity(self, user):
        """Récupère l'activité récente de l'utilisateur."""
        # Simulation d'activité - à implémenter avec un système de logs
        activities = [
            {
                'type': 'project_view',
                'title': 'Consultation de projet',
                'description': 'Vous avez consulté le projet "Développement Rural"',
                'date': datetime.now() - timedelta(hours=2),
                'icon': 'fa-eye'
            },
            {
                'type': 'project_follow',
                'title': 'Suivi de projet',
                'description': 'Vous suivez maintenant le projet "Education Numérique"',
                'date': datetime.now() - timedelta(days=1),
                'icon': 'fa-heart'
            },
            {
                'type': 'notification',
                'title': 'Nouvelle notification',
                'description': 'Mise à jour sur le projet "Santé Communautaire"',
                'date': datetime.now() - timedelta(days=2),
                'icon': 'fa-bell'
            }
        ]
        return activities

    def _get_user_notifications(self, user):
        """Récupère les notifications pour l'utilisateur."""
        # Simulation de notifications - à implémenter avec un système de notifications
        notifications = [
            {
                'type': 'info',
                'title': 'Nouveau projet disponible',
                'message': 'Un nouveau projet dans votre région est maintenant disponible.',
                'date': datetime.now() - timedelta(hours=6),
                'read': False
            },
            {
                'type': 'success',
                'title': 'Projet terminé avec succès',
                'message': 'Le projet "Infrastructure Rurale" a été terminé avec succès.',
                'date': datetime.now() - timedelta(days=3),
                'read': True
            },
            {
                'type': 'warning',
                'title': 'Mise à jour requise',
                'message': 'Veuillez mettre à jour vos informations de profil.',
                'date': datetime.now() - timedelta(days=7),
                'read': False
            }
        ]
        return notifications

    def _get_recommended_projects(self, user, user_projects):
        """Récupère les projets recommandés pour l'utilisateur."""
        Project = request.env['sama.promis.project'].sudo()
        
        # Recommandations basées sur les types de projets de l'utilisateur
        user_project_types = list(set(p.project_type for p in user_projects))
        
        recommended = Project.search([
            ('state', 'in', ['approved', 'in_progress']),
            ('project_type', 'in', user_project_types),
            ('id', 'not in', [p.id for p in user_projects])
        ], limit=4, order='create_date desc')
        
        # Si pas assez de recommandations, ajouter des projets populaires
        if len(recommended) < 4:
            additional = Project.search([
                ('state', 'in', ['approved', 'in_progress']),
                ('priority', 'in', ['high', 'urgent']),
                ('id', 'not in', [p.id for p in user_projects] + recommended.ids)
            ], limit=4 - len(recommended), order='total_budget desc')
            recommended = recommended + additional
        
        return recommended

    @http.route(['/promispublic/citizen/follow/<int:project_id>'], 
                type='json', auth="user", website=True)
    def follow_project(self, project_id, **kw):
        """Permet à un utilisateur de suivre un projet."""
        Project = request.env['sama.promis.project'].sudo()
        project = Project.browse(project_id)
        
        if not project.exists():
            return {'success': False, 'message': 'Projet non trouvé'}
        
        # Ici, implémenter la logique de suivi
        # Pour l'instant, simulation
        return {
            'success': True, 
            'message': f'Vous suivez maintenant le projet "{project.name}"'
        }

    @http.route(['/promispublic/citizen/unfollow/<int:project_id>'], 
                type='json', auth="user", website=True)
    def unfollow_project(self, project_id, **kw):
        """Permet à un utilisateur de ne plus suivre un projet."""
        Project = request.env['sama.promis.project'].sudo()
        project = Project.browse(project_id)
        
        if not project.exists():
            return {'success': False, 'message': 'Projet non trouvé'}
        
        # Ici, implémenter la logique de désuivi
        return {
            'success': True, 
            'message': f'Vous ne suivez plus le projet "{project.name}"'
        }

    @http.route(['/promispublic/citizen/notifications/mark_read'], 
                type='json', auth="user", website=True)
    def mark_notifications_read(self, notification_ids=None, **kw):
        """Marque les notifications comme lues."""
        # Ici, implémenter la logique de marquage des notifications
        return {'success': True, 'message': 'Notifications marquées comme lues'}

    @http.route(['/promispublic/citizen/profile'], 
                type='http', auth="user", website=True)
    def citizen_profile(self, **kw):
        """Page de profil citoyen."""
        user = request.env.user
        
        values = {
            'user': user,
            'company_name': request.env.company.name or "SAMA ETAT",
            'page_title': f'Mon Profil - {user.name}',
        }
        
        return request.render('sama_promis.citizen_profile', values)

    @http.route(['/promispublic/citizen/activity'], 
                type='http', auth="user", website=True)
    def citizen_activity(self, **kw):
        """Page d'activité détaillée du citoyen."""
        user = request.env.user
        
        # Activité complète de l'utilisateur
        full_activity = self._get_user_recent_activity(user)
        
        values = {
            'user': user,
            'activities': full_activity,
            'company_name': request.env.company.name or "SAMA ETAT",
            'page_title': f'Mon Activité - {user.name}',
        }
        
        return request.render('sama_promis.citizen_activity', values)

    @http.route(['/promispublic/citizen/api/stats'], 
                type='json', auth="user", website=True)
    def get_citizen_stats(self, **kw):
        """API pour récupérer les statistiques du citoyen."""
        user = request.env.user
        Project = request.env['sama.promis.project'].sudo()
        
        # Projets liés à l'utilisateur
        user_projects = []
        if user.partner_id:
            user_projects = Project.search([
                '|',
                ('partner_id', '=', user.partner_id.id),
                ('implementing_partner_ids', 'in', [user.partner_id.id])
            ])
        
        stats = {
            'my_projects': len(user_projects),
            'active_projects': len([p for p in user_projects if p.state == 'in_progress']),
            'completed_projects': len([p for p in user_projects if p.state == 'completed']),
            'total_budget': sum(p.total_budget for p in user_projects),
            'notifications_count': 3,  # Simulation
            'following_count': 5,  # Simulation
        }
        
        return stats