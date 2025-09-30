# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta

class DashboardController(http.Controller):
    @http.route(['/dashboard', '/dashboard/page/<int:page>'], type='http', auth="public", website=True)
    def dashboard(self, page=1, **kw):
        # Get project data with enhanced filtering
        Project = request.env['project.project'].sudo()
        domain = []
        
        # Apply filters from URL parameters
        project_type = kw.get('project_type')
        if project_type:
            domain.append(('project_type', '=', project_type))
        
        donor_id = kw.get('donor_id')
        if donor_id:
            domain.append(('donor_id', '=', int(donor_id)))
        
        state = kw.get('state')
        if state:
            domain.append(('state', '=', state))
        
        # Count total projects
        total_projects = Project.search_count(domain)
        
        # Count projects by status
        projects_by_status = {}
        for state_value, state_label in Project._fields['state'].selection:
            count = Project.search_count(domain + [('state', '=', state_value)])
            if count > 0:
                projects_by_status[state_label] = count
        
        # Count active projects
        active_projects = Project.search_count(domain + [('state', '=', 'in_progress')])
        
        # Calculate budget utilization
        projects = Project.search(domain)
        total_budget = sum(project.total_budget for project in projects if hasattr(project, 'total_budget') and project.total_budget)
        utilized_budget = total_budget * 0.5  # Placeholder calculation
        budget_utilized = (utilized_budget / total_budget * 100) if total_budget > 0 else 0
        
        # Get donor statistics
        donors = request.env['res.partner'].sudo().search([
            ('is_donor', '=', True),
            ('is_company', '=', True)
        ])
        
        donor_stats = []
        for donor in donors:
            donor_projects = Project.search([('donor_id', '=', donor.id)])
            donor_budget = sum(p.total_budget for p in donor_projects if p.total_budget)
            donor_stats.append({
                'name': donor.name,
                'project_count': len(donor_projects),
                'total_budget': donor_budget,
            })
        
        # Get upcoming events
        upcoming_events = 0
        if 'calendar.event' in request.env:
            upcoming_events = request.env['calendar.event'].sudo().search_count([
                ('start', '>=', fields.Datetime.now()),
                ('start', '<=', fields.Datetime.add(fields.Datetime.now(), days=30))
            ])
        
        # Get recent projects with pagination
        page_size = 10
        pager = request.website.pager(
            url='/dashboard',
            total=total_projects,
            page=page,
            step=page_size,
            scope=7,
            url_args=kw
        )
        
        projects = Project.search(domain, limit=page_size, offset=pager['offset'], order='create_date desc')
        
        # Get project types for filtering
        project_types = dict(Project._fields['project_type'].selection)
        
        # Get states for filtering
        project_states = dict(Project._fields['state'].selection)
        
        values = {
            'projects': projects,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'budget_utilized': round(budget_utilized, 1),
            'upcoming_events': upcoming_events,
            'pager': pager,
            'projects_by_status': projects_by_status,
            'donor_stats': donor_stats,
            'project_types': project_types,
            'project_states': project_states,
            'donors': donors,
            'current_filters': kw,
        }
        
        return request.render('sama_promis.sama_promis_dashboard', values)

    @http.route(['/dashboard/project/<model("project.project"):project>'], type='http', auth="public", website=True)
    def project_detail(self, project, **kw):
        """Public project detail page"""
        if not project:
            return request.not_found()
        
        # Get project details
        project_data = {
            'project': project,
            'donor': project.donor_id,
            'manager': project.user_id,
            'performance_indicators': project.performance_indicator_ids,
            'evaluations': project.evaluation_ids,
        }
        
        return request.render('sama_promis.project_detail', project_data)

    @http.route(['/dashboard/donor/<model("res.partner"):donor>'], type='http', auth="public", website=True)
    def donor_detail(self, donor, **kw):
        """Public donor detail page"""
        if not donor or not donor.is_donor:
            return request.not_found()
        
        # Get donor projects
        Project = request.env['project.project'].sudo()
        donor_projects = Project.search([('donor_id', '=', donor.id)])
        
        donor_data = {
            'donor': donor,
            'projects': donor_projects,
            'total_projects': len(donor_projects),
            'total_budget': sum(p.total_budget for p in donor_projects if p.total_budget),
        }
        
        return request.render('sama_promis.donor_detail', donor_data)

    @http.route(['/dashboard/api/stats'], type='json', auth="public")
    def get_stats(self, **kw):
        """API endpoint for dashboard statistics"""
        Project = request.env['project.project'].sudo()
        
        # Get basic stats
        total_projects = Project.search_count([])
        active_projects = Project.search_count([('state', '=', 'in_progress')])
        
        # Get budget stats
        projects = Project.search([])
        total_budget = sum(project.total_budget for project in projects if project.total_budget)
        
        # Get projects by type
        projects_by_type = {}
        for project_type, label in Project._fields['project_type'].selection:
            count = Project.search_count([('project_type', '=', project_type)])
            if count > 0:
                projects_by_type[label] = count
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_budget': total_budget,
            'projects_by_type': projects_by_type,
        }
