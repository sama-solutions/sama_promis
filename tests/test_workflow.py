# -*- coding: utf-8 -*-
"""Tests pour les workflows des projets SAMA PROMIS."""

from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProjectWorkflow(TransactionCase):
    """Valide les transitions de workflow d'un projet."""

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Workflow Partner',
        })
        self.project = self.env['sama.promis.project'].create({
            'name': 'Workflow Project',
            'project_type': 'education',
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
        })

    def test_full_workflow(self):
        """Le projet doit suivre le cycle de vie complet sans erreurs."""
        self.assertEqual(self.project.state, 'draft')

        self.project.action_submit_for_review()
        self.assertEqual(self.project.state, 'submitted')

        self.project.action_start_review()
        self.assertEqual(self.project.state, 'under_review')

        self.project.action_approve_project()
        self.assertEqual(self.project.state, 'approved')

        self.project.action_start_implementation()
        self.assertEqual(self.project.state, 'in_progress')

        self.project.action_complete_project()
        self.assertEqual(self.project.state, 'completed')
        self.assertTrue(self.project.state_history)

    def test_resume_after_suspension(self):
        """Un projet suspendu peut être repris."""
        self.project.action_submit_for_review()
        self.project.action_start_review()
        self.project.action_approve_project()
        self.project.action_start_implementation()

        self.project.action_suspend_project()
        self.assertEqual(self.project.state, 'suspended')

        self.project.action_resume_project()
        self.assertEqual(self.project.state, 'in_progress')
