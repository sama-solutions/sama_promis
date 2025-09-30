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


@tagged('post_install', '-at_install')
class TestComplianceTaskWorkflow(TransactionCase):
    """Validate compliance task workflow lifecycle and transitions."""

    def setUp(self):
        super().setUp()
        self.compliance_profile = self.env['sama.promis.compliance.profile'].create({
            'name': 'Test Compliance Profile',
            'code': 'TEST_PROF',
            'reporting_frequency': 'quarterly',
            'reminder_days_before': 7,
            'escalation_days_after': 3,
        })
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'is_donor': True,
        })
        
        self.project = self.env['sama.promis.project'].create({
            'name': 'Compliance Workflow Project',
            'project_type': 'development',
            'partner_id': self.partner.id,
            'donor_id': self.partner.id,
            'total_budget': 100000,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'compliance_profile_id': self.compliance_profile.id,
            'use_compliance_profile': True,
        })
        
        self.task = self.env['sama.promis.compliance.task'].create({
            'name': 'Test Compliance Task',
            'project_id': self.project.id,
            'compliance_profile_id': self.compliance_profile.id,
            'task_type': 'report',
            'priority': 'normal',
            'deadline': date.today() + timedelta(days=30),
        })

    def _assert_task_state(self, expected):
        self.task.flush()
        self.task.invalidate_recordset(['state'])
        self.assertEqual(self.task.state, expected)

    def test_compliance_task_full_workflow(self):
        """A compliance task should follow the full lifecycle without errors."""
        self._assert_task_state('pending')

        self.task.write({'state': 'in_progress'})
        self._assert_task_state('in_progress')

        self.task.write({'state': 'submitted'})
        self._assert_task_state('submitted')

        self.task.write({'state': 'under_review'})
        self._assert_task_state('under_review')

        self.task.action_approve()
        self._assert_task_state('approved')
        self.assertTrue(self.task.approved_by)
        self.assertTrue(self.task.approval_date)

    def test_compliance_task_direct_completion(self):
        """A task can be marked completed directly."""
        self.task.write({'state': 'in_progress'})
        self.task.action_mark_completed()
        self._assert_task_state('completed')
        self.assertTrue(self.task.actual_completion_date)

    def test_compliance_task_rejection(self):
        """A task can be rejected and sent back to in_progress."""
        self.task.write({'state': 'in_progress'})
        self.task.write({'state': 'submitted'})
        self._assert_task_state('submitted')

        self.task.action_reject()
        self._assert_task_state('in_progress')

    def test_compliance_task_requires_document_validation(self):
        """Tasks requiring documents should validate before submission."""
        from odoo.exceptions import ValidationError
        
        task_with_doc = self.env['sama.promis.compliance.task'].create({
            'name': 'Document Required Task',
            'project_id': self.project.id,
            'task_type': 'deliverable',
            'priority': 'high',
            'deadline': date.today() + timedelta(days=15),
            'requires_document': True,
        })

        task_with_doc.write({'state': 'in_progress'})
        
        # Should fail without documents
        with self.assertRaises(ValidationError):
            task_with_doc.write({'state': 'submitted'})

    def test_compliance_task_overdue_calculation(self):
        """Overdue status should be correctly calculated."""
        overdue_task = self.env['sama.promis.compliance.task'].create({
            'name': 'Overdue Task',
            'project_id': self.project.id,
            'task_type': 'milestone',
            'deadline': date.today() - timedelta(days=5),
        })

        overdue_task._compute_overdue_status()
        self.assertTrue(overdue_task.is_overdue)
        self.assertEqual(overdue_task.days_overdue, 5)

    def test_compliance_task_days_until_deadline(self):
        """Days until deadline should be correctly calculated."""
        future_task = self.env['sama.promis.compliance.task'].create({
            'name': 'Future Task',
            'project_id': self.project.id,
            'task_type': 'checklist',
            'deadline': date.today() + timedelta(days=7),
        })

        future_task._compute_days_until_deadline()
        self.assertEqual(future_task.days_until_deadline, 7)

    def test_compliance_task_approval_workflow(self):
        """Tasks requiring approval should follow approval workflow."""
        approval_task = self.env['sama.promis.compliance.task'].create({
            'name': 'Approval Task',
            'project_id': self.project.id,
            'task_type': 'approval',
            'deadline': date.today() + timedelta(days=20),
            'requires_approval': True,
        })

        approval_task.write({'state': 'in_progress'})
        approval_task.write({'state': 'submitted'})
        approval_task.write({'state': 'under_review'})
        
        approval_task.action_approve()
        self._assert_task_state('approved')
        self.assertTrue(approval_task.approved_by)
        self.assertTrue(approval_task.approval_date)

    def test_contract_compliance_statistics_update(self):
        """Contract compliance statistics should update when tasks change."""
        contract = self.env['sama.promis.contract'].create({
            'name': 'CT-WORKFLOW-001',
            'project_id': self.project.id,
            'partner_id': self.partner.id,
            'contract_type': 'grant',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'amount': 50000,
        })

        # Create tasks
        tasks = []
        for i in range(5):
            task = self.env['sama.promis.compliance.task'].create({
                'name': f'Contract Task {i+1}',
                'contract_id': contract.id,
                'project_id': self.project.id,
                'task_type': 'report',
                'deadline': date.today() + timedelta(days=30+i),
            })
            tasks.append(task)

        # Complete some tasks
        tasks[0].action_mark_completed()
        tasks[1].action_mark_completed()
        tasks[2].action_mark_completed()

        contract._compute_compliance_statistics()
        self.assertEqual(contract.compliance_task_count, 5)
        self.assertEqual(contract.compliance_tasks_completed, 3)
        self.assertEqual(contract.compliance_rate, 60.0)

    def test_project_compliance_statistics_update(self):
        """Project compliance statistics should update when tasks change."""
        # Create tasks
        for i in range(4):
            self.env['sama.promis.compliance.task'].create({
                'name': f'Project Task {i+1}',
                'project_id': self.project.id,
                'task_type': 'milestone',
                'deadline': date.today() + timedelta(days=60+i*10),
            })

        # Complete all tasks
        for task in self.project.compliance_task_ids:
            task.action_mark_completed()

        self.project._compute_compliance_statistics()
        self.assertGreater(self.project.compliance_task_count, 0)
        self.assertEqual(self.project.compliance_rate, 100.0)
        self.assertEqual(self.project.overdue_compliance_tasks, 0)
