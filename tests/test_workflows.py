# -*- coding: utf-8 -*-
"""Odoo workflow tests for SAMA PROMIS projects."""

from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProjectWorkflow(TransactionCase):
    """Validate the project workflow lifecycle and guards."""

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Workflow Partner',
        })
        self.project = self.env['sama.promis.project'].create({
            'name': 'Workflow Project',
            'project_type': 'education',
            'partner_id': self.partner.id,
            'total_budget': 10000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=120),
        })

    def _assert_state(self, expected):
        self.project.flush()
        self.project.invalidate_recordset(['state'])
        self.assertEqual(self.project.state, expected)

    def test_full_workflow_happy_path(self):
        """A project should follow the full lifecycle without errors."""
        self._assert_state('draft')

        self.project.action_submit_for_review()
        self._assert_state('submitted')
        self.assertTrue(self.project.submission_date)

        self.project.action_start_review()
        self._assert_state('under_review')

        self.project.action_approve_project()
        self._assert_state('approved')
        self.assertTrue(self.project.approval_date)

        self.project.action_start_implementation()
        self._assert_state('in_progress')
        self.assertTrue(self.project.actual_start_date)

        self.project.action_complete_project()
        self._assert_state('completed')
        self.assertTrue(self.project.state_history)
        self.assertTrue(self.project.actual_end_date)

    def test_suspend_and_resume(self):
        """Suspension should be reversible back to in progress."""
        self.project.action_submit_for_review()
        self.project.action_start_review()
        self.project.action_approve_project()
        self.project.action_start_implementation()
        self._assert_state('in_progress')

        self.project.action_suspend_project()
        self._assert_state('suspended')

        self.project.action_resume_project()
        self._assert_state('in_progress')

    def test_resume_without_suspension_is_idempotent(self):
        """Resuming a non-suspended project should safely keep it in progress."""
        self.project.action_start_implementation()
        self._assert_state('in_progress')

        # Calling resume directly should not raise and should keep in progress
        self.project.action_resume_project()
        self._assert_state('in_progress')

    def test_cancel_from_any_state(self):
        """Cancelling should move to the cancelled state regardless of progress."""
        self.project.action_submit_for_review()
        self.project.action_cancel_project()
        self._assert_state('cancelled')
