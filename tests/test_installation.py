# -*- coding: utf-8 -*-
"""Tests d'installation pour le module SAMA PROMIS."""
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSamaPromisInstallation(TransactionCase):
    """Valide l'installation complète du module."""

    def test_module_data_loaded(self):
        """Vérifie que les données de base sont chargées."""
        project_count = self.env['sama.promis.project'].search_count([])
        self.assertGreater(project_count, 0, "Les projets de démonstration doivent être chargés.")

    def test_menus_available(self):
        """Vérifie que les menus principaux existent."""
        action = self.env.ref('sama_promis.action_sama_promis_project', raise_if_not_found=False)
        self.assertIsNotNone(action, "L'action du menu projets doit être disponible.")

    def test_security_rules(self):
        """Vérifie la présence des règles d'accès."""
        access_rules = self.env['ir.model.access'].search([
            ('name', 'ilike', 'sama'),
        ])
        self.assertTrue(access_rules, "Les règles d'accès doivent être configurées.")
