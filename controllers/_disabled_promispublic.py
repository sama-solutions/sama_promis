# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Dashboard Public "PROMISPUBLIC"
=============================================

Contrôleur pour le dashboard public avec cartes, filtres et navigation moderne.
Inspiré de SAMA ETAT avec les fonctionnalités spécifiques à SAMA PROMIS.
"""

from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
import json


class PromisPublicController(http.Controller):
    """Contrôleur pour le dashboard public PROMISPUBLIC."""

    @http.route(['/promispublic', '/promispublic/page/<int:page>'], 
                type='http', auth="public", website=True)
    def promispublic_dashboard(self, page=1, **kw):
        """
        Dashboard public principal "PROMISPUBLIC".
        
        Affiche:
        - Cartes avec filtres (inspiré SAMA ETAT)
        - Statistiques en temps réel
        - Projets avec pagination
        - Navigation moderne
        """
        # Récupération des modèles
        Project = request.env['sama.promis.project'].sudo()
        Partner = request.env['res.partner'].sudo()
        
        # Construction du domaine de recherche
        domain = [('state', 'in', ['approved', 'in_progress', 'completed'])]  # Projets publics
        
        # Application des filtres
        project_type = kw.get('project_type')
        if project_type:
            domain.append(('project_type', '=', project_type))
        
        donor_id = kw.get('donor_id')
        if donor_id:
            try:
                domain.append(('donor_id', '=', int(donor_id)))
            except ValueError:
                pass
        
        state = kw.get('state')
        if state:
            domain.append(('state', '=', state))
        
        region = kw.get('region')
        if region:
            domain.append(('region', 'ilike', region))
        
        # Recherche textuelle
        search = kw.get('search')
        if search:
            domain.extend([
                '|', '|', '|',
                ('name', 'ilike', search),
                ('description', 'ilike', search),
                ('objectives', 'ilike', search),
                ('partner_id.name', 'ilike', search)
            ])
        
        # Statistiques globales
        total_projects = Project.search_count(domain)
        all_projects = Project.search(domain)
        
        # Calcul des métriques
        total_budget = sum(all_projects.mapped('total_budget'))
        spent_budget = sum(all_projects.mapped('spent_amount'))
        active_projects = len(all_projects.filtered(lambda p: p.state == 'in_progress'))
        completed_projects = len(all_projects.filtered(lambda p: p.state == 'completed'))
        
        # Statistiques par état
        state_stats = {}
        for state_value, state_label in Project._fields['state'].selection:
            if state_value in ['approved', 'in_progress', 'completed']:
                count = len(all_projects.filtered(lambda p: p.state == state_value))
                state_stats[state_value] = {
                    'label': state_label,
                    'count': count,
                    'percentage': (count / total_projects * 100) if total_projects > 0 else 0
                }
        
        # Statistiques par type
        type_stats = {}
        for type_value, type_label in Project._fields['project_type'].selection:
            count = len(all_projects.filtered(lambda p: p.project_type == type_value))
            type_stats[type_value] = {
                'label': type_label,
                'count': count,
                'percentage': (count / total_projects * 100) if total_projects > 0 else 0
            }
        
        # Statistiques par bailleur
        donor_stats = []
        donors = all_projects.mapped('donor_id')
        for donor in donors:
            donor_projects = all_projects.filtered(lambda p: p.donor_id == donor)
            donor_budget = sum(donor_projects.mapped('total_budget'))
            donor_stats.append({
                'donor': donor,
                'project_count': len(donor_projects),
                'total_budget': donor_budget,
                'percentage': (donor_budget / total_budget * 100) if total_budget > 0 else 0
            })
        donor_stats = sorted(donor_stats, key=lambda x: x['total_budget'], reverse=True)[:5]
        
        # Pagination
        page_size = 12
        pager = request.website.pager(
            url='/promispublic',
            total=total_projects,
            page=page,
            step=page_size,
            scope=7,
            url_args=kw
        )
        
        # Projets pour la page actuelle
        projects = Project.search(
            domain, 
            limit=page_size, 
            offset=pager['offset'], 
            order='create_date desc'
        )
        
        # Données pour les filtres
        project_types = dict(Project._fields['project_type'].selection)
        project_states = {
            'approved': 'Approuvé',
            'in_progress': 'En Cours',
            'completed': 'Terminé'
        }
        donors = Partner.search([('is_donor', '=', True)], order='name')
        regions = list(set(all_projects.mapped('region'))) if all_projects else []
        regions = [r for r in regions if r]  # Supprimer les valeurs vides
        
        # Projets récents et en vedette
        recent_projects = Project.search(
            domain + [('create_date', '>=', fields.Datetime.now() - timedelta(days=30))],
            limit=6,
            order='create_date desc'
        )
        
        featured_projects = Project.search(
            domain + [('priority', 'in', ['high', 'urgent'])],
            limit=6,
            order='priority desc, total_budget desc'
        )
        
        # Nom de l'entreprise pour le titre
        company_name = request.env.company.name or "SAMA ETAT"
        
        values = {
            # Données principales
            'projects': projects,
            'total_projects': total_projects,
            'pager': pager,
            
            # Statistiques
            'total_budget': total_budget,
            'spent_budget': spent_budget,
            'budget_utilization': (spent_budget / total_budget * 100) if total_budget > 0 else 0,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'state_stats': state_stats,
            'type_stats': type_stats,
            'donor_stats': donor_stats,
            
            # Projets spéciaux
            'recent_projects': recent_projects,
            'featured_projects': featured_projects,
            
            # Filtres
            'project_types': project_types,
            'project_states': project_states,
            'donors': donors,
            'regions': regions,
            'current_filters': kw,
            
            # Configuration
            'company_name': company_name,
            'page_title': f'PROMIS PUBLIC et {company_name}',
            
            # Métadonnées
            'last_update': datetime.now().strftime('%d/%m/%Y à %H:%M'),
        }
        
        return request.render('sama_promis.promispublic_dashboard', values)

    @http.route(['/promispublic/project/<model("sama.promis.project"):project>'], 
                type='http', auth="public", website=True)
    def project_detail(self, project, **kw):
        """Page de détail d'un projet."""
        if not project or project.state not in ['approved', 'in_progress', 'completed']:
            return request.not_found()
        
        # Projets similaires
        similar_projects = request.env['sama.promis.project'].sudo().search([
            ('id', '!=', project.id),
            ('project_type', '=', project.project_type),
            ('state', 'in', ['approved', 'in_progress', 'completed']),
        ], limit=4)
        
        values = {
            'project': project,
            'similar_projects': similar_projects,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.project_detail_public', values)

    @http.route(['/promispublic/donor/<model("res.partner"):donor>'], 
                type='http', auth="public", website=True)
    def donor_detail(self, donor, **kw):
        """Page de détail d'un bailleur."""
        if not donor or not donor.is_donor:
            return request.not_found()
        
        # Projets du bailleur
        projects = request.env['sama.promis.project'].sudo().search([
            ('donor_id', '=', donor.id),
            ('state', 'in', ['approved', 'in_progress', 'completed']),
        ], order='create_date desc')
        
        # Statistiques du bailleur
        total_budget = sum(projects.mapped('total_budget'))
        active_projects = len(projects.filtered(lambda p: p.state == 'in_progress'))
        completed_projects = len(projects.filtered(lambda p: p.state == 'completed'))
        
        values = {
            'donor': donor,
            'projects': projects,
            'total_projects': len(projects),
            'total_budget': total_budget,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.donor_detail_public', values)

    @http.route(['/promispublic/api/stats'], type='json', auth="public")
    def get_statistics(self, **kw):
        """API pour récupérer les statistiques en JSON."""
        Project = request.env['sama.promis.project'].sudo()
        
        # Projets publics
        domain = [('state', 'in', ['approved', 'in_progress', 'completed'])]
        projects = Project.search(domain)
        
        # Statistiques de base
        stats = {
            'total_projects': len(projects),
            'active_projects': len(projects.filtered(lambda p: p.state == 'in_progress')),
            'completed_projects': len(projects.filtered(lambda p: p.state == 'completed')),
            'total_budget': sum(projects.mapped('total_budget')),
            'spent_budget': sum(projects.mapped('spent_amount')),
        }
        
        # Statistiques par type
        stats['by_type'] = {}
        for ptype, label in Project._fields['project_type'].selection:
            count = len(projects.filtered(lambda p: p.project_type == ptype))
            stats['by_type'][ptype] = {'label': label, 'count': count}
        
        # Statistiques par état
        stats['by_state'] = {}
        for state in ['approved', 'in_progress', 'completed']:
            count = len(projects.filtered(lambda p: p.state == state))
            label = dict(Project._fields['state'].selection)[state]
            stats['by_state'][state] = {'label': label, 'count': count}
        
        return stats

    @http.route(['/promispublic/api/projects'], type='json', auth="public")
    def get_projects_data(self, **kw):
        """API pour récupérer les données des projets."""
        Project = request.env['sama.promis.project'].sudo()
        
        domain = [('state', 'in', ['approved', 'in_progress', 'completed'])]
        projects = Project.search(domain, limit=50, order='create_date desc')
        
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'reference': project.reference,
                'type': project.project_type,
                'state': project.state,
                'budget': project.total_budget,
                'progress': project.progress_percentage,
                'donor': project.donor_id.name if project.donor_id else '',
                'region': project.region or '',
                'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else '',
                'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else '',
            })
        
        return projects_data

    @http.route(['/promispublic/search'], type='http', auth="public", website=True)
    def search_projects(self, **kw):
        """Recherche avancée de projets."""
        search_term = kw.get('q', '')
        
        if not search_term:
            return request.redirect('/promispublic')
        
        # Redirection vers le dashboard avec le terme de recherche
        return request.redirect(f'/promispublic?search={search_term}')

    @http.route(['/promispublic/export'], type='http', auth="public")
    def export_projects(self, format='csv', **kw):
        """Export des données de projets."""
        Project = request.env['sama.promis.project'].sudo()
        
        domain = [('state', 'in', ['approved', 'in_progress', 'completed'])]
        projects = Project.search(domain)
        
        if format == 'json':
            # Export JSON
            data = []
            for project in projects:
                data.append({
                    'reference': project.reference,
                    'name': project.name,
                    'type': project.project_type,
                    'state': project.state,
                    'budget': project.total_budget,
                    'donor': project.donor_id.name if project.donor_id else '',
                    'region': project.region or '',
                })
            
            response = request.make_response(
                json.dumps(data, indent=2, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Content-Disposition', 'attachment; filename="projets_sama_promis.json"')
                ]
            )
            return response
        
        # Export CSV par défaut
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow([
            'Référence', 'Nom', 'Type', 'État', 'Budget', 
            'Bailleur', 'Région', 'Date Début', 'Date Fin'
        ])
        
        # Données
        for project in projects:
            writer.writerow([
                project.reference or '',
                project.name or '',
                dict(Project._fields['project_type'].selection).get(project.project_type, ''),
                dict(Project._fields['state'].selection).get(project.state, ''),
                project.total_budget or 0,
                project.donor_id.name if project.donor_id else '',
                project.region or '',
                project.start_date.strftime('%d/%m/%Y') if project.start_date else '',
                project.end_date.strftime('%d/%m/%Y') if project.end_date else '',
            ])
        
        response = request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', 'attachment; filename="projets_sama_promis.csv"')
            ]
        )
        return response