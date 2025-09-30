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
        ProcurementPlan = request.env['sama.promis.procurement.plan'].sudo()
        CallForProposal = request.env['sama.promis.call.for.proposal'].sudo()
        Event = request.env['sama.promis.event'].sudo()
        ComplianceTask = request.env['sama.promis.compliance.task'].sudo()
        FundingSource = request.env['sama.promis.project.funding.source'].sudo()
        
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
        
        # Statistiques supplémentaires pour procurement, calls, events
        procurement_plans = ProcurementPlan.search([('state', 'in', ['validated', 'in_execution', 'completed'])])
        active_procurements = len(procurement_plans.filtered(lambda p: p.state == 'in_execution'))
        
        calls_for_proposals = CallForProposal.search([('state', 'in', ['open', 'evaluation'])])
        open_calls = len(calls_for_proposals.filtered(lambda c: c.state == 'open'))
        
        upcoming_events = Event.search([('event_date', '>=', fields.Datetime.now())])
        events_count = len(upcoming_events)
        
        # Compliance statistics
        compliance_tasks = ComplianceTask.search([])
        total_compliance = len(compliance_tasks)
        completed_compliance = len(compliance_tasks.filtered(lambda t: t.state == 'completed'))
        compliance_rate = (completed_compliance / total_compliance * 100) if total_compliance > 0 else 0
        
        # Funding sources breakdown
        funding_sources = FundingSource.search([('project_id', 'in', all_projects.ids)])
        international_funding = sum(funding_sources.filtered(lambda f: f.funding_origin == 'international').mapped('amount'))
        local_funding = sum(funding_sources.filtered(lambda f: f.funding_origin == 'local').mapped('amount'))
        
        # Budget utilization by region
        region_stats = {}
        for region_name in set(all_projects.mapped('region')):
            if region_name:
                region_projects = all_projects.filtered(lambda p: p.region == region_name)
                region_stats[region_name] = {
                    'count': len(region_projects),
                    'budget': sum(region_projects.mapped('total_budget'))
                }
        
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
            
            # Statistiques supplémentaires
            'procurement_plans': procurement_plans[:6],  # Top 6 for display
            'active_procurements': active_procurements,
            'calls_for_proposals': calls_for_proposals[:6],
            'open_calls': open_calls,
            'upcoming_events': upcoming_events[:6],
            'events_count': events_count,
            'compliance_rate': compliance_rate,
            'international_funding': international_funding,
            'local_funding': local_funding,
            'region_stats': region_stats,
            
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
        
        # Funding sources breakdown
        funding_sources = project.funding_source_ids
        
        # Procurement plans linked to project
        procurement_plans = request.env['sama.promis.procurement.plan'].sudo().search([
            ('project_id', '=', project.id),
            ('state', 'in', ['validated', 'in_execution', 'completed'])
        ])
        
        # Compliance tasks
        compliance_tasks = request.env['sama.promis.compliance.task'].sudo().search([
            ('project_id', '=', project.id)
        ])
        
        # Contracts linked to project
        contracts = request.env['sama.promis.contract'].sudo().search([
            ('project_id', '=', project.id)
        ])
        
        # Payments linked to project
        payments = request.env['sama.promis.payment'].sudo().search([
            ('project_id', '=', project.id)
        ])
        
        values = {
            'project': project,
            'similar_projects': similar_projects,
            'funding_sources': funding_sources,
            'procurement_plans': procurement_plans,
            'compliance_tasks': compliance_tasks,
            'contracts': contracts,
            'payments': payments,
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
        """API pour récupérer les données des projets avec pagination et filtres."""
        Project = request.env['sama.promis.project'].sudo()
        
        # Base domain
        domain = [('state', 'in', ['approved', 'in_progress', 'completed'])]
        
        # Apply filters from query parameters
        project_type = kw.get('project_type')
        if project_type:
            domain.append(('project_type', '=', project_type))
        
        donor_id = kw.get('donor_id')
        if donor_id:
            try:
                domain.append(('donor_id', '=', int(donor_id)))
            except (ValueError, TypeError):
                pass
        
        state = kw.get('state')
        if state:
            domain.append(('state', '=', state))
        
        region = kw.get('region')
        if region:
            domain.append(('region', 'ilike', region))
        
        search_term = kw.get('search') or kw.get('q')
        if search_term:
            domain.extend([
                '|', '|', '|',
                ('name', 'ilike', search_term),
                ('description', 'ilike', search_term),
                ('objectives', 'ilike', search_term),
                ('partner_id.name', 'ilike', search_term)
            ])
        
        # Pagination parameters
        try:
            page = int(kw.get('page', 1))
        except (ValueError, TypeError):
            page = 1
        
        page_size = 12
        offset = (page - 1) * page_size
        
        # Get total count
        total_count = Project.search_count(domain)
        
        # Get projects for current page
        projects = Project.search(
            domain, 
            limit=page_size, 
            offset=offset, 
            order='create_date desc'
        )
        
        # Build projects data
        projects_data = []
        for project in projects:
            # Get state label
            state_label = dict(Project._fields['state'].selection).get(project.state, project.state)
            state_class = 'success' if project.state == 'completed' else 'info' if project.state == 'in_progress' else 'warning'
            
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'code': project.reference or '',
                'reference': project.reference or '',
                'type': project.project_type,
                'state': project.state,
                'state_label': state_label,
                'state_class': state_class,
                'budget': project.total_budget,
                'progress': project.progress_percentage,
                'donor': project.donor_id.name if project.donor_id else '',
                'region': project.region or '',
                'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else '',
                'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else '',
            })
        
        # Calculate if there are more pages
        has_more = (offset + page_size) < total_count
        
        return {
            'projects': projects_data,
            'has_more': has_more,
            'total': total_count,
            'page': page,
            'page_size': page_size
        }

    @http.route(['/promispublic/search'], type='json', auth="public")
    def search_projects(self, **kw):
        """Recherche avancée de projets - retourne JSON pour AJAX."""
        search_term = kw.get('q', '')
        
        if not search_term or len(search_term) < 2:
            return {'projects': [], 'total': 0}
        
        Project = request.env['sama.promis.project'].sudo()
        
        # Build search domain
        domain = [
            ('state', 'in', ['approved', 'in_progress', 'completed']),
            '|', '|', '|',
            ('name', 'ilike', search_term),
            ('description', 'ilike', search_term),
            ('objectives', 'ilike', search_term),
            ('partner_id.name', 'ilike', search_term)
        ]
        
        # Search projects
        projects = Project.search(domain, limit=20, order='create_date desc')
        
        # Build response data
        projects_data = []
        for project in projects:
            state_label = dict(Project._fields['state'].selection).get(project.state, project.state)
            state_class = 'success' if project.state == 'completed' else 'info' if project.state == 'in_progress' else 'warning'
            
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'code': project.reference or '',
                'reference': project.reference or '',
                'type': project.project_type,
                'state': project.state,
                'state_label': state_label,
                'state_class': state_class,
                'budget': project.total_budget,
                'progress': project.progress_percentage,
                'donor': project.donor_id.name if project.donor_id else '',
                'region': project.region or '',
            })
        
        return {
            'projects': projects_data,
            'total': len(projects_data)
        }

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

    @http.route(['/promispublic/procurement'], type='http', auth='public', website=True)
    def procurement_opportunities(self, **kw):
        """Liste des opportunités de passation de marchés."""
        ProcurementPlan = request.env['sama.promis.procurement.plan'].sudo()
        
        domain = [('state', 'in', ['validated', 'in_execution', 'completed'])]
        
        # Filtres
        method = kw.get('method')
        if method:
            domain.append(('procurement_line_ids.procurement_method', '=', method))
        
        procurement_plans = ProcurementPlan.search(domain, order='create_date desc')
        
        values = {
            'procurement_plans': procurement_plans,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.procurement_list_public', values)

    @http.route(['/promispublic/procurement/<model("sama.promis.procurement.plan"):plan>'], 
                type='http', auth='public', website=True)
    def procurement_detail(self, plan, **kw):
        """Page de détail d'un plan de passation."""
        if not plan or plan.state not in ['validated', 'in_execution', 'completed']:
            return request.not_found()
        
        values = {
            'plan': plan,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.procurement_detail_public', values)

    @http.route(['/promispublic/calls'], type='http', auth='public', website=True)
    def calls_for_proposals(self, **kw):
        """Liste des appels à propositions."""
        CallForProposal = request.env['sama.promis.call.for.proposal'].sudo()
        
        domain = [('state', 'in', ['open', 'evaluation', 'awarded'])]
        
        # Filtres
        call_type = kw.get('type')
        if call_type:
            domain.append(('call_type', '=', call_type))
        
        calls = CallForProposal.search(domain, order='deadline desc')
        
        values = {
            'calls': calls,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.calls_list_public', values)

    @http.route(['/promispublic/call/<model("sama.promis.call.for.proposal"):call>'], 
                type='http', auth='public', website=True)
    def call_detail(self, call, **kw):
        """Page de détail d'un appel à propositions."""
        if not call:
            return request.not_found()
        
        values = {
            'call': call,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.call_detail_public', values)

    @http.route(['/promispublic/events'], type='http', auth='public', website=True)
    def events_list(self, **kw):
        """Liste des événements."""
        Event = request.env['sama.promis.event'].sudo()
        
        domain = [('event_date', '>=', fields.Datetime.now())]
        
        # Filtres
        event_type = kw.get('type')
        if event_type:
            domain.append(('event_type', '=', event_type))
        
        events = Event.search(domain, order='event_date asc')
        
        values = {
            'events': events,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.events_list_public', values)

    @http.route(['/promispublic/event/<model("sama.promis.event"):event>'], 
                type='http', auth='public', website=True)
    def event_detail(self, event, **kw):
        """Page de détail d'un événement."""
        if not event:
            return request.not_found()
        
        values = {
            'event': event,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.event_detail_public', values)

    @http.route(['/promispublic/funding'], type='http', auth='public', website=True)
    def funding_overview(self, **kw):
        """Vue d'ensemble des financements."""
        FundingSource = request.env['sama.promis.project.funding.source'].sudo()
        Project = request.env['sama.promis.project'].sudo()
        
        # Projets publics
        projects = Project.search([('state', 'in', ['approved', 'in_progress', 'completed'])])
        funding_sources = FundingSource.search([('project_id', 'in', projects.ids)])
        
        # Statistiques
        international_funding = sum(funding_sources.filtered(lambda f: f.funding_origin == 'international').mapped('amount'))
        local_funding = sum(funding_sources.filtered(lambda f: f.funding_origin == 'local').mapped('amount'))
        
        # Par bailleur
        donors = {}
        for source in funding_sources:
            donor = source.source_id
            if donor:
                if donor.id not in donors:
                    donors[donor.id] = {
                        'donor': donor,
                        'total': 0,
                        'projects': set()
                    }
                donors[donor.id]['total'] += source.amount
                donors[donor.id]['projects'].add(source.project_id.id)
        
        donor_list = sorted(donors.values(), key=lambda x: x['total'], reverse=True)
        
        values = {
            'international_funding': international_funding,
            'local_funding': local_funding,
            'total_funding': international_funding + local_funding,
            'donors': donor_list,
            'company_name': request.env.company.name or "SAMA ETAT",
        }
        
        return request.render('sama_promis.funding_overview_public', values)

    @http.route(['/promispublic/api/timeline'], type='json', auth='public')
    def get_timeline_data(self, **kw):
        """API pour récupérer les données de timeline."""
        Project = request.env['sama.promis.project'].sudo()
        
        projects = Project.search([('state', 'in', ['approved', 'in_progress', 'completed'])])
        
        timeline_data = []
        for project in projects:
            if project.start_date:
                timeline_data.append({
                    'id': project.id,
                    'name': project.name,
                    'start': project.start_date.strftime('%Y-%m-%d'),
                    'end': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    'state': project.state,
                })
        
        return timeline_data

    @http.route(['/promispublic/api/map'], type='json', auth='public')
    def get_map_data(self, **kw):
        """API pour récupérer les données de carte."""
        Project = request.env['sama.promis.project'].sudo()
        
        projects = Project.search([('state', 'in', ['approved', 'in_progress', 'completed'])])
        
        map_data = []
        for project in projects:
            if project.region:
                map_data.append({
                    'id': project.id,
                    'name': project.name,
                    'region': project.region,
                    'budget': project.total_budget,
                    'state': project.state,
                })
        
        return map_data

    @http.route(['/promispublic/api/charts'], type='json', auth='public')
    def get_charts_data(self, chart_type='project_types', **kw):
        """API pour récupérer les données formatées pour Chart.js."""
        Project = request.env['sama.promis.project'].sudo()
        FundingSource = request.env['sama.promis.project.funding.source'].sudo()
        
        projects = Project.search([('state', 'in', ['approved', 'in_progress', 'completed'])])
        
        if chart_type == 'project_types':
            # Distribution par type de projet
            type_counts = {}
            for ptype, label in Project._fields['project_type'].selection:
                count = len(projects.filtered(lambda p: p.project_type == ptype))
                if count > 0:
                    type_counts[label] = count
            
            return {
                'labels': list(type_counts.keys()),
                'values': list(type_counts.values())
            }
        
        elif chart_type == 'budget_by_donor':
            # Budget par bailleur
            donor_budgets = {}
            for project in projects:
                if project.donor_id:
                    donor_name = project.donor_id.name
                    if donor_name not in donor_budgets:
                        donor_budgets[donor_name] = 0
                    donor_budgets[donor_name] += project.total_budget
            
            # Top 5 bailleurs
            sorted_donors = sorted(donor_budgets.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'labels': [d[0] for d in sorted_donors],
                'values': [d[1] for d in sorted_donors]
            }
        
        elif chart_type == 'timeline':
            # Projets par mois
            from collections import defaultdict
            monthly_counts = defaultdict(int)
            
            for project in projects:
                if project.create_date:
                    month_key = project.create_date.strftime('%Y-%m')
                    monthly_counts[month_key] += 1
            
            sorted_months = sorted(monthly_counts.items())
            
            return {
                'labels': [m[0] for m in sorted_months],
                'values': [m[1] for m in sorted_months]
            }
        
        return {'labels': [], 'values': []}