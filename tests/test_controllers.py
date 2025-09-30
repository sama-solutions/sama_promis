# -*- coding: utf-8 -*-
"""HTTP controller tests for SAMA PROMIS dashboards and public portal."""

from odoo.tests import HttpCase, tagged
from unittest import skip


class ControllerTestMixin:
    """Helper mixin providing JSON-capable requests."""

    def _json_get(self, url_path):
        response = self.url_open(f"{url_path}?json=1")
        self.assertEqual(response.status_code, 200, msg=url_path)
        return response.json()


@tagged('post_install', '-at_install')
class TestInternalDashboardController(ControllerTestMixin, HttpCase):
    """Validate the internal dashboard routes and APIs."""

    def test_dashboard_route_is_available(self):
        response = self.url_open('/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_stats_api_returns_expected_keys(self):
        payload = self._json_get('/dashboard/api/stats')
        for key in ('total_projects', 'active_projects', 'total_budget', 'projects_by_type'):
            self.assertIn(key, payload)


@skip('Public portal disabled - to be developed later')
@tagged('post_install', '-at_install')
class TestPromisPublicController(ControllerTestMixin, HttpCase):
    """Validate the public PROMIS portal routes and APIs."""

    def test_promispublic_home_route(self):
        response = self.url_open('/promispublic')
        self.assertEqual(response.status_code, 200)

    def test_promispublic_stats_api(self):
        payload = self._json_get('/promispublic/api/stats')
        for key in ('total_projects', 'by_type', 'by_state'):
            self.assertIn(key, payload)

    def test_promispublic_projects_api(self):
        payload = self._json_get('/promispublic/api/projects')
        self.assertIsInstance(payload, list)
        if payload:
            self.assertIn('id', payload[0])

    def test_promispublic_export_json_route(self):
        response = self.url_open('/promispublic/export?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'application/json')
