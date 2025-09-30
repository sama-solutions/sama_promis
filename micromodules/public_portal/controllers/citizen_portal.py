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

    # =========================================================================
    # REQUESTOR PORTAL ROUTES
    # =========================================================================

    @http.route(['/my/promis', '/my/promis/page/<int:page>'], 
                type='http', auth='user', website=True)
    def requestor_portal_dashboard(self, page=1, **kw):
        """Main requestor portal dashboard."""
        user = request.env.user
        
        # Check portal access
        if not user.has_group('base.group_portal'):
            return request.redirect('/web/login')
        
        partner = user.partner_id
        if not partner:
            return request.not_found()
        
        Project = request.env['sama.promis.project'].sudo()
        Contract = request.env['sama.promis.contract'].sudo()
        ComplianceTask = request.env['sama.promis.compliance.task'].sudo()
        Payment = request.env['sama.promis.payment'].sudo()
        
        # Get user's projects
        projects = Project.search([
            '|', '|',
            ('partner_id', '=', partner.id),
            ('implementing_partner_ids', 'in', [partner.id]),
            ('donor_id', '=', partner.id)
        ])
        
        # Get user's contracts
        contracts = Contract.search([
            ('contractor_id', '=', partner.id)
        ])
        
        # Get user's compliance tasks
        compliance_tasks = ComplianceTask.search([
            ('responsible_id', '=', partner.id)
        ])
        
        # Get user's payments
        payments = Payment.search([
            ('beneficiary_id', '=', partner.id)
        ])
        
        # Calculate statistics
        stats = {
            'total_projects': len(projects),
            'active_projects': len(projects.filtered(lambda p: p.state == 'in_progress')),
            'total_contracts': len(contracts),
            'active_contracts': len(contracts.filtered(lambda c: c.state in ['draft', 'in_progress'])),
            'pending_tasks': len(compliance_tasks.filtered(lambda t: t.state in ['pending', 'in_progress'])),
            'overdue_tasks': len(compliance_tasks.filtered(lambda t: t.state == 'overdue')),
            'total_received': sum(payments.filtered(lambda p: p.state == 'paid').mapped('amount')),
            'pending_payments': sum(payments.filtered(lambda p: p.state in ['pending', 'approved']).mapped('amount')),
        }
        
        # Recent activity
        recent_activity = []
        
        # Add recent projects
        for project in projects.sorted('create_date', reverse=True)[:3]:
            recent_activity.append({
                'type': 'project',
                'title': f'Projet: {project.name}',
                'date': project.create_date,
                'icon': 'fa-project-diagram',
                'url': f'/my/promis/projects'
            })
        
        # Add recent payments
        for payment in payments.sorted('payment_date', reverse=True)[:3]:
            recent_activity.append({
                'type': 'payment',
                'title': f'Paiement: {payment.amount} FCFA',
                'date': payment.payment_date,
                'icon': 'fa-money-bill',
                'url': f'/my/promis/payments'
            })
        
        # Sort by date
        recent_activity = sorted(recent_activity, key=lambda x: x['date'], reverse=True)[:10]
        
        # Upcoming deadlines
        upcoming_deadlines = compliance_tasks.filtered(
            lambda t: t.deadline and t.deadline >= fields.Date.today() and t.state != 'completed'
        ).sorted('deadline')[:5]
        
        values = {
            'user': user,
            'partner': partner,
            'projects': projects[:6],
            'contracts': contracts[:6],
            'compliance_tasks': compliance_tasks[:6],
            'payments': payments[:6],
            'stats': stats,
            'recent_activity': recent_activity,
            'upcoming_deadlines': upcoming_deadlines,
            'page_title': 'Mon Portail PROMIS',
        }
        
        return request.render('sama_promis.requestor_portal_dashboard', values)

    @http.route(['/my/promis/projects'], type='http', auth='user', website=True)
    def requestor_projects(self, **kw):
        """List of user's projects."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        Project = request.env['sama.promis.project'].sudo()
        
        projects = Project.search([
            '|', '|',
            ('partner_id', '=', partner.id),
            ('implementing_partner_ids', 'in', [partner.id]),
            ('donor_id', '=', partner.id)
        ], order='create_date desc')
        
        values = {
            'user': user,
            'partner': partner,
            'projects': projects,
            'page_title': 'Mes Projets',
        }
        
        return request.render('sama_promis.requestor_projects', values)

    @http.route(['/my/promis/proposals'], type='http', auth='user', website=True)
    def requestor_proposals(self, **kw):
        """List of user's proposals."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        # Note: This assumes a proposal/application tracking system exists
        # For now, we'll show calls for proposals
        CallForProposal = request.env['sama.promis.call.for.proposal'].sudo()
        
        calls = CallForProposal.search([
            ('state', 'in', ['open', 'evaluation', 'awarded'])
        ], order='deadline desc')
        
        values = {
            'user': user,
            'partner': partner,
            'calls': calls,
            'page_title': 'Mes Propositions',
        }
        
        return request.render('sama_promis.requestor_proposals', values)

    @http.route(['/my/promis/contracts'], type='http', auth='user', website=True)
    def requestor_contracts(self, **kw):
        """List of user's contracts."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        Contract = request.env['sama.promis.contract'].sudo()
        
        contracts = Contract.search([
            ('contractor_id', '=', partner.id)
        ], order='contract_date desc')
        
        values = {
            'user': user,
            'partner': partner,
            'contracts': contracts,
            'page_title': 'Mes Contrats',
        }
        
        return request.render('sama_promis.requestor_contracts', values)

    @http.route(['/my/promis/compliance'], type='http', auth='user', website=True)
    def requestor_compliance(self, **kw):
        """List of user's compliance tasks."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        ComplianceTask = request.env['sama.promis.compliance.task'].sudo()
        
        tasks = ComplianceTask.search([
            ('responsible_id', '=', partner.id)
        ], order='deadline asc')
        
        # Group by state
        pending_tasks = tasks.filtered(lambda t: t.state == 'pending')
        in_progress_tasks = tasks.filtered(lambda t: t.state == 'in_progress')
        overdue_tasks = tasks.filtered(lambda t: t.state == 'overdue')
        completed_tasks = tasks.filtered(lambda t: t.state == 'completed')
        
        # Calculate compliance rate
        total_tasks = len(tasks)
        completed_count = len(completed_tasks)
        compliance_rate = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        values = {
            'user': user,
            'partner': partner,
            'tasks': tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'completed_tasks': completed_tasks,
            'compliance_rate': compliance_rate,
            'page_title': 'Mes Tâches de Conformité',
        }
        
        return request.render('sama_promis.requestor_compliance', values)

    @http.route(['/my/promis/payments'], type='http', auth='user', website=True)
    def requestor_payments(self, **kw):
        """List of user's payments."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        Payment = request.env['sama.promis.payment'].sudo()
        
        payments = Payment.search([
            ('beneficiary_id', '=', partner.id)
        ], order='payment_date desc')
        
        # Calculate totals
        total_received = sum(payments.filtered(lambda p: p.state == 'paid').mapped('amount'))
        total_pending = sum(payments.filtered(lambda p: p.state in ['pending', 'approved']).mapped('amount'))
        
        values = {
            'user': user,
            'partner': partner,
            'payments': payments,
            'total_received': total_received,
            'total_pending': total_pending,
            'page_title': 'Mes Paiements',
        }
        
        return request.render('sama_promis.requestor_payments', values)

    @http.route(['/my/promis/upload'], type='http', auth='user', methods=['POST'], csrf=True)
    def requestor_upload_document(self, **kw):
        """Handle document upload for compliance tasks."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.redirect('/my/promis')
        
        task_id = kw.get('task_id')
        uploaded_file = kw.get('file')
        
        if not task_id or not uploaded_file:
            return request.redirect('/my/promis/compliance?error=missing_data')
        
        ComplianceTask = request.env['sama.promis.compliance.task'].sudo()
        task = ComplianceTask.browse(int(task_id))
        
        if not task.exists() or task.responsible_id != partner:
            return request.redirect('/my/promis/compliance?error=unauthorized')
        
        # Save the file as attachment
        Attachment = request.env['ir.attachment'].sudo()
        attachment = Attachment.create({
            'name': uploaded_file.filename,
            'datas': uploaded_file.read(),
            'res_model': 'sama.promis.compliance.task',
            'res_id': task.id,
        })
        
        # Send notification to admin
        # TODO: Implement notification system
        
        return request.redirect(f'/my/promis/compliance?success=uploaded')

    @http.route(['/my/promis/notifications'], type='http', auth='user', website=True)
    def requestor_notifications(self, **kw):
        """Notification preferences page."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        values = {
            'user': user,
            'partner': partner,
            'page_title': 'Préférences de Notification',
        }
        
        return request.render('sama_promis.requestor_notifications', values)

    @http.route(['/my/promis/profile'], type='http', auth='user', website=True)
    def requestor_profile(self, **kw):
        """User profile page."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        values = {
            'user': user,
            'partner': partner,
            'page_title': 'Mon Profil',
        }
        
        return request.render('sama_promis.requestor_profile', values)

    @http.route(['/my/promis/activity'], type='http', auth='user', website=True)
    def requestor_activity(self, **kw):
        """Activity timeline page."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return request.not_found()
        
        # Build activity timeline
        activities = []
        
        # Add project activities
        Project = request.env['sama.promis.project'].sudo()
        projects = Project.search([
            '|', '|',
            ('partner_id', '=', partner.id),
            ('implementing_partner_ids', 'in', [partner.id]),
            ('donor_id', '=', partner.id)
        ])
        
        for project in projects:
            activities.append({
                'type': 'project',
                'title': f'Projet créé: {project.name}',
                'date': project.create_date,
                'icon': 'fa-project-diagram',
                'description': project.description or '',
            })
        
        # Add contract activities
        Contract = request.env['sama.promis.contract'].sudo()
        contracts = Contract.search([('contractor_id', '=', partner.id)])
        
        for contract in contracts:
            activities.append({
                'type': 'contract',
                'title': f'Contrat signé: {contract.name}',
                'date': contract.contract_date,
                'icon': 'fa-file-contract',
                'description': f'Montant: {contract.contract_amount} FCFA',
            })
        
        # Add payment activities
        Payment = request.env['sama.promis.payment'].sudo()
        payments = Payment.search([('beneficiary_id', '=', partner.id)])
        
        for payment in payments:
            activities.append({
                'type': 'payment',
                'title': f'Paiement reçu: {payment.amount} FCFA',
                'date': payment.payment_date,
                'icon': 'fa-money-bill',
                'description': payment.description or '',
            })
        
        # Sort by date
        activities = sorted(activities, key=lambda x: x['date'], reverse=True)
        
        values = {
            'user': user,
            'partner': partner,
            'activities': activities,
            'page_title': 'Mon Activité',
        }
        
        return request.render('sama_promis.requestor_activity', values)

    @http.route(['/my/promis/api/stats'], type='json', auth='user')
    def requestor_api_stats(self, **kw):
        """API endpoint for requestor statistics."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return {}
        
        Project = request.env['sama.promis.project'].sudo()
        Contract = request.env['sama.promis.contract'].sudo()
        ComplianceTask = request.env['sama.promis.compliance.task'].sudo()
        Payment = request.env['sama.promis.payment'].sudo()
        
        projects = Project.search([
            '|', '|',
            ('partner_id', '=', partner.id),
            ('implementing_partner_ids', 'in', [partner.id]),
            ('donor_id', '=', partner.id)
        ])
        
        contracts = Contract.search([('contractor_id', '=', partner.id)])
        tasks = ComplianceTask.search([('responsible_id', '=', partner.id)])
        payments = Payment.search([('beneficiary_id', '=', partner.id)])
        
        return {
            'total_projects': len(projects),
            'active_projects': len(projects.filtered(lambda p: p.state == 'in_progress')),
            'total_contracts': len(contracts),
            'pending_tasks': len(tasks.filtered(lambda t: t.state in ['pending', 'in_progress'])),
            'total_received': sum(payments.filtered(lambda p: p.state == 'paid').mapped('amount')),
        }

    @http.route(['/my/promis/api/notifications'], type='json', auth='user')
    def requestor_api_notifications(self, **kw):
        """API endpoint for requestor notifications."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return {'count': 0, 'notifications': []}
        
        # TODO: Implement actual notification system
        # For now, return mock data
        notifications = [
            {
                'id': 1,
                'type': 'info',
                'title': 'Nouvelle tâche de conformité',
                'message': 'Une nouvelle tâche vous a été assignée',
                'date': fields.Datetime.now().isoformat(),
                'read': False
            },
            {
                'id': 2,
                'type': 'success',
                'title': 'Paiement effectué',
                'message': 'Un paiement a été effectué sur votre compte',
                'date': fields.Datetime.now().isoformat(),
                'read': False
            }
        ]
        
        return {
            'count': len([n for n in notifications if not n['read']]),
            'notifications': notifications
        }

    @http.route(['/my/promis/api/tasks'], type='json', auth='user')
    def requestor_api_tasks(self, **kw):
        """API endpoint for upcoming tasks."""
        user = request.env.user
        partner = user.partner_id
        
        if not partner:
            return []
        
        ComplianceTask = request.env['sama.promis.compliance.task'].sudo()
        
        tasks = ComplianceTask.search([
            ('responsible_id', '=', partner.id),
            ('state', 'in', ['pending', 'in_progress']),
            ('deadline', '>=', fields.Date.today())
        ], order='deadline asc', limit=10)
        
        return [{
            'id': task.id,
            'name': task.name,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'priority': task.priority,
            'state': task.state,
        } for task in tasks]