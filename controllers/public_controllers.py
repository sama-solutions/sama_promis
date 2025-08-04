from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
import base64
import qrcode
from PIL import Image, ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

class SamaEtatController(http.Controller):

    def _generate_qr_code_with_logo(self, url):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=6) # Increased border
        qr.add_data(url)
        qr.make(fit=True)
        # Do not use RoundedModuleDrawer here, we will draw rounded patterns manually
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        # --- Start: Rounding finder patterns ---
        draw = ImageDraw.Draw(img)
        qr_width, qr_height = img.size
        box_size = 10 # From qrcode.QRCode
        border = 6 # From qrcode.QRCode
        finder_pattern_outer_size = 7 * box_size
        finder_pattern_inner_size = 5 * box_size
        finder_pattern_center_size = 3 * box_size

        # Top-left finder pattern
        outer_x = border * box_size
        outer_y = border * box_size
        draw.ellipse((outer_x, outer_y, outer_x + finder_pattern_outer_size - 1, outer_y + finder_pattern_outer_size - 1), fill="black") # 7x7 black outer circle
        draw.ellipse((outer_x + box_size, outer_y + box_size, outer_x + box_size + finder_pattern_inner_size - 1, outer_y + box_size + finder_pattern_inner_size - 1), fill="white") # 5x5 white inner circle
        # Draw central 3x3 black circle
        center_x1 = outer_x + 2 * box_size
        center_y1 = outer_y + 2 * box_size
        center_x2 = center_x1 + finder_pattern_center_size - 1
        center_y2 = center_y1 + finder_pattern_center_size - 1
        draw.ellipse((center_x1, center_y1, center_x2, center_y2), fill="black")

        # Top-right finder pattern
        outer_x = qr_width - (border * box_size + finder_pattern_outer_size)
        outer_y = border * box_size
        draw.ellipse((outer_x, outer_y, outer_x + finder_pattern_outer_size - 1, outer_y + finder_pattern_outer_size - 1), fill="black") # 7x7 black outer circle
        draw.ellipse((outer_x + box_size, outer_y + box_size, outer_x + box_size + finder_pattern_inner_size - 1, outer_y + box_size + finder_pattern_inner_size - 1), fill="white") # 5x5 white inner circle
        # Draw central 3x3 black circle
        center_x1 = outer_x + 2 * box_size
        center_y1 = outer_y + 2 * box_size
        center_x2 = center_x1 + finder_pattern_center_size - 1
        center_y2 = center_y1 + finder_pattern_center_size - 1
        draw.ellipse((center_x1, center_y1, center_x2, center_y2), fill="black")

        # Bottom-left finder pattern
        outer_x = border * box_size
        outer_y = qr_height - (border * box_size + finder_pattern_outer_size)
        draw.ellipse((outer_x, outer_y, outer_x + finder_pattern_outer_size - 1, outer_y + finder_pattern_outer_size - 1), fill="black") # 7x7 black outer circle
        draw.ellipse((outer_x + box_size, outer_y + box_size, outer_x + box_size + finder_pattern_inner_size - 1, outer_y + box_size + finder_pattern_inner_size - 1), fill="white") # 5x5 white inner circle
        # Draw central 3x3 black circle
        center_x1 = outer_x + 2 * box_size
        center_y1 = outer_y + 2 * box_size
        center_x2 = center_x1 + finder_pattern_center_size - 1
        center_y2 = center_y1 + finder_pattern_center_size - 1
        draw.ellipse((center_x1, center_y1, center_x2, center_y2), fill="black")
        # --- End: Rounding finder patterns ---

        # Load logo and resize
        logo_path = '/home/grand-as/psagsn/custom_addons/sama_etat/logo.png'
        logo = Image.open(logo_path).convert("RGBA")

        # Calculate logo size and position with padding
        qr_width, qr_height = img.size
        logo_desired_size = qr_width // 4  # Adjust as needed
        padding = 2 * 10 # 2 dots of whitespace, assuming box_size=10
        logo_area_size = logo_desired_size + padding

        logo = logo.resize((logo_desired_size, logo_desired_size), Image.LANCZOS)

        logo_pos_x = (qr_width - logo_area_size) // 2
        logo_pos_y = (qr_height - logo_area_size) // 2

        # Create a new image with a white background, then paste QR code and logo
        img_final = Image.new("RGBA", img.size, (255, 255, 255, 255)) # Solid white background for the final image
        img_final.paste(img, (0, 0)) # Paste QR code onto the white background

        # Create a white square for the logo area
        logo_area = Image.new("RGBA", (logo_area_size, logo_area_size), (255, 255, 255, 255))

        # Create a circular mask for the logo area
        mask = Image.new("L", (logo_area_size, logo_area_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, logo_area_size, logo_area_size), fill=255)

        # Calculate position to paste the actual logo onto the logo_area (centered)
        logo_paste_x = (logo_area_size - logo_desired_size) // 2
        logo_paste_y = (logo_area_size - logo_desired_size) // 2

        # Paste logo onto its white background, preserving alpha, and apply circular mask
        logo_area.paste(logo, (logo_paste_x, logo_paste_y), logo)
        img_final.paste(logo_area, (logo_pos_x, logo_pos_y), mask)

        import io
        buffered = io.BytesIO()
        img_final.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @http.route('/senegal2050/dashboard', type='http', auth='public', website=True)
    def public_dashboard(self, **kw):
        dashboard_data = request.env['senegal.plan.dashboard'].sudo().get_dashboard()

        # Generate QR code for the dashboard URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        dashboard_url = f"{base_url}/senegal2050/dashboard"
        qr_code_base64 = self._generate_qr_code_with_logo(dashboard_url)

        recent_projects = request.env['government.project'].sudo().search([], order='create_date desc', limit=9)

        return request.render('sama_etat.modern_public_dashboard_page', {
            'total_projects': dashboard_data.total_projects,
            'active_projects': dashboard_data.active_projects,
            'total_ministries': dashboard_data.total_ministries,
            'upcoming_events': dashboard_data.upcoming_events,
            'completed_projects': dashboard_data.completed_projects,
            'public_decisions': dashboard_data.published_decisions,
            'dashboard_url': dashboard_url,
            'qr_code': qr_code_base64,
            'recent_projects': recent_projects,
        })

    @http.route('/senegal2050/project/<int:project_id>', type='http', auth='public', website=True)
    def public_project_page(self, project_id, **kw):
        project = request.env['government.project'].sudo().browse(project_id).read(['name', 'description', 'project_code', 'status', 'priority', 'ministry_id', 'manager_id', 'start_date', 'end_date', 'progress', 'strategic_objective_id', 'budget_id', 'task_count', 'write_date', 'latitude', 'longitude'])[0]
        if not project:
            return request.render('website.404')
            return request.render('website.404')

        # Generate QR code for the project URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        project_url = f"{base_url}/senegal2050/project/{project_id}"
        qr_code_base64 = self._generate_qr_code_with_logo(project_url)

        return request.render('sama_etat.public_project_page', {
            'project': project,
            'project_url': project_url,
            'qr_code': qr_code_base64,
        })

    @http.route('/senegal2050/ministry/<int:ministry_id>', type='http', auth='public', website=True)
    def public_ministry_page(self, ministry_id, **kw):
        ministry = request.env['government.ministry'].sudo().browse(ministry_id)
        if not ministry.exists():
            return request.render('website.404')

        # Generate QR code for the ministry URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ministry_url = f"{base_url}/senegal2050/ministry/{ministry_id}"
        qr_code_base64 = self._generate_qr_code_with_logo(ministry_url)

        return request.render('sama_etat.public_ministry_page', {
            'ministry': ministry,
            'ministry_url': ministry_url,
            'qr_code': qr_code_base64,
            'projects': ministry.project_ids.filtered(lambda p: p.status != 'draft'), # Only show non-draft projects
        })

    @http.route('/senegal2050/decision/<int:decision_id>', type='http', auth='public', website=True)
    def public_decision_page(self, decision_id, **kw):
        decision = request.env['government.decision'].sudo().browse(decision_id).read(['name', 'title', 'reference', 'decision_type', 'decision_date', 'document', 'document_name', 'description', 'status', 'strategic_objective_id', 'project_id', 'event_id', 'ministry_id', 'is_public', 'implementation_status', 'implementation_deadline', 'responsible_user_id', 'progress_percentage', 'last_follow_up_date', 'next_follow_up_date', 'follow_up_notes', 'is_on_track', 'days_until_deadline', 'latitude', 'longitude'])[0]
        if not decision:
            return request.render('website.404')
            return request.render('website.404')

        # Generate QR code for the decision URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        decision_url = f"{base_url}/senegal2050/decision/{decision_id}"
        qr_code_base64 = self._generate_qr_code_with_logo(decision_url)

        return request.render('sama_etat.public_decision_page', {
            'decision': decision,
            'decision_url': decision_url,
            'qr_code': qr_code_base64,
        })

    @http.route('/senegal2050/event/<int:event_id>', type='http', auth='public', website=True)
    def public_event_page(self, event_id, **kw):
        event_data = request.env['government.event'].sudo().browse(event_id).read(['name', 'event_date', 'date_start', 'date_end', 'location', 'organizer_id', 'event_type', 'description', 'project_id', 'strategic_objective_id', 'status', 'odoo_event_id', 'latitude', 'longitude'])
        if not event_data:
            return request.render('website.404')
        event = event_data[0]
        if not event:
            return request.render('website.404')
            return request.render('website.404')

        # Generate QR code for the event URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        event_url = f"{base_url}/senegal2050/event/{event_id}"
        qr_code_base64 = self._generate_qr_code_with_logo(event_url)

        return request.render('sama_etat.public_event_page', {
            'event': event,
            'event_url': event_url,
            'qr_code': qr_code_base64,
        })

    @http.route('/senegal2050/objective/<int:objective_id>', type='http', auth='public', website=True)
    def public_objective_page(self, objective_id, **kw):
        objective = request.env['strategic.objective'].sudo().browse(objective_id).read(['name', 'code', 'axis_id', 'description', 'kpi_ids', 'linked_projects', 'linked_decisions', 'linked_budgets', 'linked_events'])[0]
        if not objective:
            return request.render('website.404')

        # Generate QR code for the objective URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        objective_url = f"{base_url}/senegal2050/objective/{objective_id}"
        qr_code_base64 = self._generate_qr_code_with_logo(objective_url)

        return request.render('sama_etat.public_objective_page', {
            'objective': objective,
            'objective_url': objective_url,
            'qr_code': qr_code_base64,
        })

    @http.route('/senegal2050/axis/<int:axis_id>', type='http', auth='public', website=True)
    def public_axis_page(self, axis_id, **kw):
        axis = request.env['strategic.axis'].sudo().browse(axis_id).read(['name', 'code', 'description', 'pillar_id', 'objective_ids'])[0]
        if not axis:
            return request.render('website.404')

        # Generate the axis URL
        axis_url = request.httprequest.url_root + f'senegal2050/axis/{axis_id}'
        qr_code_base64 = self._generate_qr_code_with_logo(axis_url)

        return request.render('sama_etat.public_axis_page', {
            'axis': axis,
            'axis_url': axis_url,
            'qr_code': qr_code_base64,
        })

    @http.route('/senegal2050/pillar/<int:pillar_id>', type='http', auth='public', website=True)
    def public_pillar_page(self, pillar_id, **kw):
        pillar = request.env['strategic.pillar'].sudo().browse(pillar_id).read(['name', 'code', 'description', 'plan_id', 'axis_ids'])[0]
        if not pillar:
            return request.render('website.404')

        # Generate the pillar URL
        pillar_url = request.httprequest.url_root + f'senegal2050/pillar/{pillar_id}'
        qr_code_base64 = self._generate_qr_code_with_logo(pillar_url)

        return request.render('sama_etat.public_pillar_page', {
            'pillar': pillar,
            'pillar_url': pillar_url,
            'qr_code': qr_code_base64,
        })

    @http.route('/sama_etat/get_map_data', type='json', auth='public', website=True)
    def get_map_data(self):
        Project = request.env['government.project'].sudo()
        Decision = request.env['government.decision'].sudo()
        Event = request.env['government.event'].sudo()

        projects = Project.search_read([('latitude', '!=', False), ('longitude', '!=', False)],
                                       ['name', 'description', 'latitude', 'longitude', 'status', 'progress', 'start_date', 'end_date', 'ministry_id', 'project_code'])
        decisions = Decision.search_read([('latitude', '!=', False), ('longitude', '!=', False)],
                                         ['name', 'title', 'description', 'latitude', 'longitude', 'decision_type', 'reference', 'decision_date', 'ministry_id', 'implementation_status'])
        events = Event.search_read([('latitude', '!=', False), ('longitude', '!=', False)],
                                     ['name', 'description', 'latitude', 'longitude', 'event_type', 'event_date', 'date_start', 'location', 'organizer_id', 'status'])

        return {
            'projects': projects,
            'decisions': decisions,
            'events': events,
        }

    @http.route('/senegal2050/fullscreen_map', type='http', auth='public', website=True)
    def fullscreen_map(self, **kw):
        return request.render('sama_etat.fullscreen_map_page', {
            'page_title': 'Carte Interactive - Plan Sénégal 2050',
        })
