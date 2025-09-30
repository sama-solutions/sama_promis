# -*- coding: utf-8 -*-
"""Tests pour le portail public citoyen."""

from datetime import date, timedelta

from odoo.tests import HttpCase, tagged
from unittest import skip


@skip('Public portal disabled - to be developed later')
@tagged('post_install', '-at_install')
class TestPublicPortal(HttpCase):
    """Valide les pages principales du portail citoyen."""

    def test_citizen_portal_home(self):
        """La page d'accueil du portail citoyen doit être accessible."""
        response = self.url_open('/promispublic')
        self.assertEqual(response.status_code, 200)

    def test_project_detail_route(self):
        """La page de détail d'un projet doit se charger pour un projet approuvé."""
        project = self.env['sama.promis.project'].create({
            'name': 'Portal Project',
            'project_type': 'education',
            'partner_id': self.env['res.partner'].create({'name': 'Portal Partner'}).id,
            'total_budget': 15000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
            'state': 'approved',
        })

        response = self.url_open(f'/promispublic/project/{project.id}')
        self.assertEqual(response.status_code, 200)

    def test_donor_detail_route(self):
        """La page de détail d'un bailleur doit afficher ses projets publics."""
        donor = self.env['res.partner'].create({
            'name': 'Portal Donor',
            'is_donor': True,
            'partner_type': 'donor',
        })
        self.env['sama.promis.project'].create({
            'name': 'Donor Project',
            'project_type': 'education',
            'partner_id': self.env['res.partner'].create({'name': 'Beneficiary'}).id,
            'donor_id': donor.id,
            'total_budget': 20000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=120),
            'state': 'in_progress',
        })

        response = self.url_open(f'/promispublic/donor/{donor.id}')
        self.assertEqual(response.status_code, 200)

    def test_project_detail_not_found_for_non_public_states(self):
        """Les projets hors états publics doivent retourner 404."""
        project = self.env['sama.promis.project'].create({
            'name': 'Private Project',
            'project_type': 'education',
            'partner_id': self.env['res.partner'].create({'name': 'Hidden Partner'}).id,
            'total_budget': 5000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=45),
            'state': 'draft',
        })

        response = self.url_open(f'/promispublic/project/{project.id}')
        self.assertEqual(response.status_code, 404)
