# -*- coding: utf-8 -*-
"""Tests fonctionnels pour les contrôleurs SAMA PROMIS."""

from odoo.tests import HttpCase, tagged
from unittest import skip


@skip('Dashboard controller disabled - to be developed later')
@tagged('post_install', '-at_install')
class TestDashboardController(HttpCase):
    """Valide les routes du tableau de bord interne."""

    def test_dashboard_route_is_available(self):
        """La route /dashboard doit répondre avec un statut HTTP 200."""
        response = self.url_open('/dashboard')
        self.assertEqual(response.status_code, 200)


@skip('Public portal disabled - to be developed later')
@tagged('post_install', '-at_install')
class TestPromisPublicController(HttpCase):
    """Valide les routes publiques PROMISPUBLIC."""

    def test_promispublic_dashboard_route(self):
        """La route principale PROMISPUBLIC doit être accessible."""
        response = self.url_open('/promispublic')
        self.assertEqual(response.status_code, 200)

    def test_promispublic_stats_api(self):
        """L'API JSON des statistiques doit renvoyer une réponse valide."""
        response = self.url_open('/promispublic/api/stats?json=1')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('total_projects', payload)
        self.assertIn('by_type', payload)
        self.assertIn('by_state', payload)
