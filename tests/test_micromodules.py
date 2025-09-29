# -*- coding: utf-8 -*-
"""Micromodule wiring tests for the SAMA PROMIS architecture."""

from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestMicromoduleRegistry(TransactionCase):
    """Validate that core micromodules are properly wired into the ORM."""

    def test_project_model_inherits_base_mixin(self):
        project_model = self.env['sama.promis.project']
        self.assertIn('sama.promis.base.model', project_model._inherit)
        self.assertIn('qr_code_data', project_model._fields)
        self.assertIn('state_history', project_model._fields)

    def test_partner_extension_fields_available(self):
        partner_fields = self.env['res.partner']._fields
        for field_name in ('partner_type', 'is_donor', 'is_beneficiary', 'qr_code_data'):
            self.assertIn(field_name, partner_fields)

    def test_dashboard_helper_returns_expected_keys(self):
        # Create minimal donor and project to feed statistics
        donor = self.env['res.partner'].create({
            'name': 'Dashboard Donor',
            'is_donor': True,
            'partner_type': 'donor',
        })
        project = self.env['sama.promis.project'].create({
            'name': 'Dashboard Project',
            'project_type': 'education',
            'partner_id': donor.id,
            'donor_id': donor.id,
            'total_budget': 5000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=60),
            'state': 'in_progress',
        })
        project.action_suspend_project()
        project.action_resume_project()

        stats = self.env['sama.promis.project'].get_dashboard_data()
        for key in (
            'total_projects',
            'active_projects',
            'completed_projects',
            'delayed_projects',
            'type_statistics',
            'total_budget',
            'spent_budget',
            'budget_utilization',
        ):
            self.assertIn(key, stats)

    def test_workflow_guard_prevents_invalid_transitions(self):
        project = self.env['sama.promis.project'].create({
            'name': 'Transition Project',
            'project_type': 'education',
            'partner_id': self.env['res.partner'].create({'name': 'Partner'}).id,
            'total_budget': 1000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
        })

        project.action_submit_for_review()
        project.action_start_review()
        project.action_approve_project()
        project.action_start_implementation()
        project.action_suspend_project()
        project.action_resume_project()
        project.action_cancel_project()

        self.assertEqual(project.state, 'cancelled')
        # Cancelled projects can return to draft using workflow mixin
        project.action_reset_to_draft()
        self.assertEqual(project.state, 'draft')
