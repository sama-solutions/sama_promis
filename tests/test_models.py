# -*- coding: utf-8 -*-
"""Tests unitaires des modèles principaux SAMA PROMIS."""

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSamaPromisProjectModel(TransactionCase):
    """Valide le comportement du modèle `sama.promis.project`."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_model = cls.env['sama.promis.project']
        cls.contract_model = cls.env['sama.promis.contract']
        cls.payment_model = cls.env['sama.promis.payment.request']
        cls.call_model = cls.env['sama.promis.call.proposal']
        cls.partner_model = cls.env['res.partner']
        cls.base_project = cls.project_model.create({
            'name': 'Projet Test Automatisé',
            'project_type': 'development',
            'partner_id': cls.env.ref('sama_promis.partner_beneficiary_1').id,
            'donor_id': cls.env.ref('sama_promis.partner_donor_1').id,
            'total_budget': 1000000,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'deadline': '2024-12-31',
        })

    def test_reference_generation(self):
        """La création du projet doit générer une référence unique."""
        self.assertTrue(self.base_project.reference)
        self.assertTrue(self.base_project.reference.startswith('SP-'))

    def test_qr_code_fields(self):
        """Les données QR code doivent être calculées.
        
        Note: QR codes now point to backend URLs temporarily until public portal is ready.
        """
        self.base_project._compute_qr_code_data()
        self.base_project._compute_qr_code_url()
        self.assertIn('/web#id=', self.base_project.qr_code_data or '', "QR code should contain backend URL format")
        self.assertIn('model=sama.promis.project', self.base_project.qr_code_data or '', "QR code should specify the model")
        self.assertEqual(self.base_project.qr_code_url, self.base_project.qr_code_data)

    def test_workflow_transitions(self):
        """Le workflow projet doit suivre les transitions définies."""
        self.base_project.action_submit_for_review()
        self.assertEqual(self.base_project.state, 'submitted')
        self.base_project.action_start_review()
        self.assertEqual(self.base_project.state, 'under_review')
        self.base_project.action_approve_project()
        self.assertEqual(self.base_project.state, 'approved')
        self.base_project.action_start_implementation()
        self.assertEqual(self.base_project.state, 'in_progress')
        self.base_project.action_suspend_project()
        self.assertEqual(self.base_project.state, 'suspended')
        self.base_project.action_resume_project()
        self.assertEqual(self.base_project.state, 'in_progress')
        self.base_project.action_complete_project()
        self.assertEqual(self.base_project.state, 'completed')

    def test_relations(self):
        """Les relations contrats et paiements doivent fonctionner."""
        contract = self.contract_model.create({
            'name': 'CT-TEST-001',
            'project_id': self.base_project.id,
            'partner_id': self.base_project.partner_id.id,
            'contract_type': 'grant',
            'start_date': '2024-01-15',
            'end_date': '2024-12-15',
            'amount': 300000,
        })
        self.assertIn(contract, self.base_project.contract_ids)
        payment = self.payment_model.create({
            'project_id': self.base_project.id,
            'contract_id': contract.id,
            'amount': 15000,
        })
        self.assertIn(payment, self.base_project.payment_ids)

    def test_state_history_tracking(self):
        """L'historique des états doit être mis à jour."""
        history = self.base_project.state_history or ''
        self.assertIn('Création', history)


@tagged('post_install', '-at_install')
class TestOtherModels(TransactionCase):
    """Valide les modèles complémentaires."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['sama.promis.project'].create({
            'name': 'Projet Workflow Paiement',
            'project_type': 'health',
            'partner_id': cls.env.ref('sama_promis.partner_beneficiary_2').id,
            'donor_id': cls.env.ref('sama_promis.partner_donor_2').id,
            'total_budget': 500000,
            'start_date': '2024-02-01',
            'end_date': '2024-12-01',
            'deadline': '2024-12-20',
        })
        cls.contract = cls.env['sama.promis.contract'].create({
            'name': 'CT-TEST-002',
            'project_id': cls.project.id,
            'partner_id': cls.project.partner_id.id,
            'contract_type': 'service',
            'start_date': '2024-02-15',
            'end_date': '2024-11-30',
            'amount': 200000,
        })

    def test_contract_states(self):
        """Le contrat doit changer d'état correctement."""
        self.contract.write({'state': 'generated'})
        self.assertEqual(self.contract.state, 'generated')
        self.contract.write({'state': 'active'})
        self.assertEqual(self.contract.state, 'active')

    def test_payment_workflow(self):
        """Le workflow des paiements doit suivre les étapes."""
        payment = self.env['sama.promis.payment.request'].create({
            'project_id': self.project.id,
            'contract_id': self.contract.id,
            'amount': 10000,
        })
        self.assertEqual(payment.state, 'draft')
        payment.action_submit()
        self.assertEqual(payment.state, 'submitted')
        payment.action_approve()
        self.assertEqual(payment.state, 'approved')

    def test_call_for_proposal_relations(self):
        """Un appel à propositions doit lier des projets."""
        call = self.env['sama.promis.call.proposal'].create({
            'name': 'CFP-AUTO',
            'title': 'Test CFP',
            'donor_id': self.env.ref('sama_promis.partner_donor_1').id,
            'submission_deadline': '2024-09-30',
            'state': 'published',
        })
        self.project.call_for_proposal_id = call.id
        self.assertEqual(self.project.call_for_proposal_id, call)

    def test_partner_extensions(self):
        """Les champs étendus des partenaires doivent être disponibles."""
        partner = self.env['res.partner'].create({
            'name': 'Partenaire Expertise',
            'partner_type': 'ngo',
            'is_ngo': True,
        })
        self.assertTrue(partner.is_ngo)
        self.assertEqual(partner.partner_type, 'ngo')


@tagged('post_install', '-at_install')
class TestMultiSourceFunding(TransactionCase):
    """Test multi-source funding functionality."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_model = cls.env['sama.promis.project']
        cls.funding_source_model = cls.env['sama.promis.project.funding.source']
        cls.partner_model = cls.env['res.partner']
        
        # Get company country for testing
        cls.company_country = cls.env.company.country_id
        
        # Create test donors with different countries
        cls.international_donor = cls.partner_model.create({
            'name': 'World Bank Test',
            'is_company': True,
            'is_donor': True,
            'donor_type': 'multilateral',
            'country_id': cls.env.ref('base.us').id,  # USA = international
        })
        
        cls.local_donor = cls.partner_model.create({
            'name': 'Gouvernement Sénégal Test',
            'is_company': True,
            'is_donor': True,
            'donor_type': 'government',
            'country_id': cls.env.ref('base.sn').id,  # Senegal = local
        })
        
        cls.beneficiary = cls.env.ref('sama_promis.partner_beneficiary_1')
        
        # Create test project
        cls.project = cls.project_model.create({
            'name': 'Projet Multi-Sources Test',
            'project_type': 'development',
            'partner_id': cls.beneficiary.id,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'use_multi_source_funding': True,
        })
    
    def test_funding_origin_classification(self):
        """Test that partners are correctly classified as international/local based on country."""
        # International donor should be classified as international
        self.international_donor._compute_funding_origin()
        self.assertEqual(self.international_donor.funding_origin, 'international')
        self.assertTrue(self.international_donor.is_international_donor)
        self.assertFalse(self.international_donor.is_local_donor)
        
        # Local donor should be classified as local
        self.local_donor._compute_funding_origin()
        self.assertEqual(self.local_donor.funding_origin, 'local')
        self.assertTrue(self.local_donor.is_local_donor)
        self.assertFalse(self.local_donor.is_international_donor)
    
    def test_create_funding_source(self):
        """Test creating a funding source and verify it's linked to the project."""
        source = self.funding_source_model.create({
            'name': 'WB Grant',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 500000,
            'funding_type': 'grant',
        })
        
        self.assertEqual(source.project_id, self.project)
        self.assertEqual(source.partner_id, self.international_donor)
        self.assertEqual(source.amount, 500000)
        self.assertIn(source, self.project.funding_source_ids)
    
    def test_total_budget_calculation(self):
        """Total budget should be sum of all funding sources."""
        # Create funding sources
        source1 = self.funding_source_model.create({
            'name': 'WB Grant',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 500000,
            'funding_type': 'grant',
        })
        source2 = self.funding_source_model.create({
            'name': 'Gov Cofinancing',
            'project_id': self.project.id,
            'partner_id': self.local_donor.id,
            'amount': 300000,
            'funding_type': 'co_financing',
        })
        
        # Trigger compute
        self.project._compute_funding_totals()
        
        # Verify total
        self.assertEqual(self.project.total_budget_computed, 800000)
        self.assertEqual(self.project.funding_sources_count, 2)
    
    def test_international_local_split(self):
        """International and local funding should be correctly split."""
        # Create funding sources
        self.funding_source_model.create({
            'name': 'WB Grant',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 500000,
            'funding_type': 'grant',
        })
        self.funding_source_model.create({
            'name': 'Gov Cofinancing',
            'project_id': self.project.id,
            'partner_id': self.local_donor.id,
            'amount': 300000,
            'funding_type': 'co_financing',
        })
        
        # Trigger compute
        self.project._compute_funding_totals()
        
        # Verify split
        self.assertEqual(self.project.total_international_funding, 500000)
        self.assertEqual(self.project.total_local_funding, 300000)
    
    def test_percentage_calculation(self):
        """Test that percentage_of_total is correctly calculated for each source."""
        source1 = self.funding_source_model.create({
            'name': 'WB Grant',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 600000,
            'funding_type': 'grant',
        })
        source2 = self.funding_source_model.create({
            'name': 'Gov Cofinancing',
            'project_id': self.project.id,
            'partner_id': self.local_donor.id,
            'amount': 400000,
            'funding_type': 'co_financing',
        })
        
        # Trigger compute
        self.project._compute_funding_totals()
        source1._compute_percentage()
        source2._compute_percentage()
        
        # Verify percentages
        self.assertEqual(source1.percentage_of_total, 60.0)
        self.assertEqual(source2.percentage_of_total, 40.0)
    
    def test_legacy_migration(self):
        """Test the action_migrate_legacy_funding method converts old data correctly."""
        # Create a project with legacy funding data
        legacy_project = self.project_model.create({
            'name': 'Legacy Project',
            'project_type': 'infrastructure',
            'partner_id': self.beneficiary.id,
            'donor_id': self.international_donor.id,
            'donor_contribution': 700000,
            'partner_contribution': 200000,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
        })
        
        # Migrate
        legacy_project.action_migrate_legacy_funding()
        
        # Verify migration
        self.assertTrue(legacy_project.use_multi_source_funding)
        self.assertEqual(len(legacy_project.funding_source_ids), 2)
        
        # Check amounts
        donor_source = legacy_project.funding_source_ids.filtered(
            lambda s: s.partner_id == self.international_donor
        )
        partner_source = legacy_project.funding_source_ids.filtered(
            lambda s: s.partner_id == self.beneficiary
        )
        
        self.assertEqual(donor_source.amount, 700000)
        self.assertEqual(partner_source.amount, 200000)
    
    def test_remaining_budget_with_multi_source(self):
        """Test that remaining_budget calculation works with multi-source funding."""
        # Create funding sources
        self.funding_source_model.create({
            'name': 'WB Grant',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 1000000,
            'funding_type': 'grant',
        })
        
        # Trigger compute
        self.project._compute_funding_totals()
        
        # Simulate spending
        self.project.spent_amount = 400000
        self.project._compute_remaining_budget()
        
        # Verify
        self.assertEqual(self.project.remaining_budget, 600000)
    
    def test_budget_utilization_with_multi_source(self):
        """Test that budget_utilization_rate calculation works with multi-source funding."""
        # Create funding sources
        self.funding_source_model.create({
            'name': 'WB Grant',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 1000000,
            'funding_type': 'grant',
        })
        
        # Trigger compute
        self.project._compute_funding_totals()
        
        # Simulate spending
        self.project.spent_amount = 250000
        self.project._compute_budget_utilization()
        
        # Verify
        self.assertEqual(self.project.budget_utilization_rate, 25.0)
    
    def test_funding_source_states(self):
        """Test the state transitions (draft -> confirmed -> received)."""
        source = self.funding_source_model.create({
            'name': 'Test Source',
            'project_id': self.project.id,
            'partner_id': self.international_donor.id,
            'amount': 500000,
            'funding_type': 'grant',
        })
        
        # Initial state
        self.assertEqual(source.state, 'draft')
        
        # Confirm
        source.action_confirm()
        self.assertEqual(source.state, 'confirmed')
        
        # Mark as received
        source.action_mark_received()
        self.assertEqual(source.state, 'received')
        self.assertTrue(source.received_date)
    
    def test_backward_compatibility(self):
        """Test that projects with use_multi_source_funding=False still work with legacy fields."""
        legacy_project = self.project_model.create({
            'name': 'Legacy Mode Project',
            'project_type': 'health',
            'partner_id': self.beneficiary.id,
            'donor_id': self.international_donor.id,
            'total_budget': 500000,
            'donor_contribution': 400000,
            'partner_contribution': 100000,
            'use_multi_source_funding': False,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
        })
        
        # Verify legacy mode works
        self.assertFalse(legacy_project.use_multi_source_funding)
        self.assertEqual(legacy_project.total_budget, 500000)
        
        # Simulate spending
        legacy_project.spent_amount = 200000
        legacy_project._compute_remaining_budget()
        legacy_project._compute_budget_utilization()
        
        # Verify calculations use legacy total_budget
        self.assertEqual(legacy_project.remaining_budget, 300000)
        self.assertEqual(legacy_project.budget_utilization_rate, 40.0)
    
    def test_funding_origin_manual_override(self):
        """Test that manual funding origin override works."""
        # Create a donor and manually set origin
        donor = self.partner_model.create({
            'name': 'Test Donor',
            'is_company': True,
            'is_donor': True,
            'donor_type': 'foundation',
            'country_id': self.env.ref('base.us').id,
            'funding_origin_manual': 'local',  # Manual override
        })
        
        donor._compute_funding_origin()
        
        # Should use manual override
        self.assertEqual(donor.funding_origin, 'local')
    
    def test_amount_positive_constraint(self):
        """Test that funding source amount must be positive."""
        with self.assertRaises(Exception):
            self.funding_source_model.create({
                'name': 'Invalid Source',
                'project_id': self.project.id,
                'partner_id': self.international_donor.id,
                'amount': -100,  # Negative amount should fail
                'funding_type': 'grant',
            })


@tagged('post_install', '-at_install')
class TestComplianceManagement(TransactionCase):
    """Test compliance profile and task functionality."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.compliance_profile_model = cls.env['sama.promis.compliance.profile']
        cls.compliance_task_model = cls.env['sama.promis.compliance.task']
        cls.project_model = cls.env['sama.promis.project']
        cls.contract_model = cls.env['sama.promis.contract']
        cls.partner_model = cls.env['res.partner']
        
        # Create test donor with compliance profile
        cls.donor = cls.partner_model.create({
            'name': 'World Bank Test',
            'is_company': True,
            'is_donor': True,
            'donor_type': 'multilateral',
            'country_id': cls.env.ref('base.us').id,
        })
        
        # Create compliance profile
        cls.compliance_profile = cls.compliance_profile_model.create({
            'name': 'World Bank Standard Compliance',
            'code': 'WB_STD_TEST',
            'reporting_frequency': 'quarterly',
            'requires_financial_report': True,
            'requires_narrative_report': True,
            'requires_indicator_report': True,
            'reminder_days_before': 7,
            'escalation_days_after': 3,
        })
        
        # Link profile to donor
        cls.donor.write({
            'compliance_profile_ids': [(4, cls.compliance_profile.id)],
            'default_compliance_profile_id': cls.compliance_profile.id,
        })
        
        # Create test project
        cls.beneficiary = cls.env.ref('sama_promis.partner_beneficiary_1')
        cls.project = cls.project_model.create({
            'name': 'Compliance Test Project',
            'project_type': 'development',
            'partner_id': cls.beneficiary.id,
            'donor_id': cls.donor.id,
            'total_budget': 1000000,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'compliance_profile_id': cls.compliance_profile.id,
            'use_compliance_profile': True,
        })
        
        # Create test contract
        cls.contract = cls.contract_model.create({
            'name': 'CT-COMPLIANCE-001',
            'project_id': cls.project.id,
            'partner_id': cls.beneficiary.id,
            'contract_type': 'grant',
            'start_date': '2024-01-15',
            'end_date': '2024-12-15',
            'amount': 500000,
        })
    
    def test_compliance_profile_creation(self):
        """Test that compliance profiles are created correctly."""
        self.assertTrue(self.compliance_profile.id)
        self.assertEqual(self.compliance_profile.code, 'WB_STD_TEST')
        self.assertEqual(self.compliance_profile.reporting_frequency, 'quarterly')
        self.assertTrue(self.compliance_profile.is_active)
    
    def test_compliance_profile_statistics(self):
        """Test that compliance profile statistics are computed."""
        self.compliance_profile._compute_statistics()
        self.assertGreaterEqual(self.compliance_profile.project_count, 1)
        self.assertGreaterEqual(self.compliance_profile.contract_count, 1)
    
    def test_compliance_task_creation(self):
        """Test creating compliance tasks."""
        task = self.compliance_task_model.create({
            'name': 'Quarterly Financial Report',
            'project_id': self.project.id,
            'contract_id': self.contract.id,
            'compliance_profile_id': self.compliance_profile.id,
            'task_type': 'report',
            'priority': 'high',
            'deadline': '2024-04-01',
            'requires_document': True,
        })
        
        self.assertTrue(task.id)
        self.assertEqual(task.state, 'pending')
        self.assertEqual(task.task_type, 'report')
        self.assertTrue(task.requires_document)
    
    def test_compliance_task_workflow(self):
        """Test compliance task state transitions."""
        task = self.compliance_task_model.create({
            'name': 'Test Milestone',
            'project_id': self.project.id,
            'task_type': 'milestone',
            'priority': 'normal',
            'deadline': '2024-06-01',
        })
        
        # Test state transitions
        self.assertEqual(task.state, 'pending')
        
        task.write({'state': 'in_progress'})
        self.assertEqual(task.state, 'in_progress')
        
        task.action_mark_completed()
        self.assertEqual(task.state, 'completed')
        self.assertTrue(task.actual_completion_date)
    
    def test_compliance_task_overdue_detection(self):
        """Test that overdue tasks are correctly identified."""
        from datetime import date, timedelta
        
        # Create task with past deadline
        past_date = date.today() - timedelta(days=5)
        task = self.compliance_task_model.create({
            'name': 'Overdue Task',
            'project_id': self.project.id,
            'task_type': 'deliverable',
            'priority': 'high',
            'deadline': past_date,
        })
        
        task._compute_overdue_status()
        self.assertTrue(task.is_overdue)
        self.assertGreater(task.days_overdue, 0)
    
    def test_compliance_task_days_until_deadline(self):
        """Test days until deadline calculation."""
        from datetime import date, timedelta
        
        future_date = date.today() + timedelta(days=10)
        task = self.compliance_task_model.create({
            'name': 'Future Task',
            'project_id': self.project.id,
            'task_type': 'checklist',
            'deadline': future_date,
        })
        
        task._compute_days_until_deadline()
        self.assertGreaterEqual(task.days_until_deadline, 9)
        self.assertLessEqual(task.days_until_deadline, 11)
    
    def test_contract_compliance_statistics(self):
        """Test that contract compliance statistics are computed."""
        # Create multiple tasks
        for i in range(5):
            self.compliance_task_model.create({
                'name': f'Task {i+1}',
                'contract_id': self.contract.id,
                'project_id': self.project.id,
                'task_type': 'report',
                'deadline': '2024-06-01',
            })
        
        # Mark some as completed
        tasks = self.contract.compliance_task_ids[:3]
        for task in tasks:
            task.action_mark_completed()
        
        self.contract._compute_compliance_statistics()
        self.assertEqual(self.contract.compliance_task_count, 5)
        self.assertEqual(self.contract.compliance_tasks_completed, 3)
        self.assertEqual(self.contract.compliance_rate, 60.0)
    
    def test_project_compliance_statistics(self):
        """Test that project compliance statistics are computed."""
        # Create tasks for project
        for i in range(4):
            self.compliance_task_model.create({
                'name': f'Project Task {i+1}',
                'project_id': self.project.id,
                'task_type': 'milestone',
                'deadline': '2024-07-01',
            })
        
        # Mark all as completed
        for task in self.project.compliance_task_ids:
            task.action_mark_completed()
        
        self.project._compute_compliance_statistics()
        self.assertGreater(self.project.compliance_task_count, 0)
        self.assertEqual(self.project.compliance_rate, 100.0)
    
    def test_compliance_task_requires_document_validation(self):
        """Test that tasks requiring documents validate before submission."""
        from odoo.exceptions import ValidationError
        
        task = self.compliance_task_model.create({
            'name': 'Document Required Task',
            'project_id': self.project.id,
            'task_type': 'deliverable',
            'deadline': '2024-05-01',
            'requires_document': True,
        })
        
        # Try to submit without documents - should fail
        with self.assertRaises(ValidationError):
            task.write({'state': 'submitted'})
    
    def test_compliance_task_approval_workflow(self):
        """Test approval workflow for compliance tasks."""
        task = self.compliance_task_model.create({
            'name': 'Approval Task',
            'project_id': self.project.id,
            'task_type': 'approval',
            'deadline': '2024-05-01',
            'requires_approval': True,
        })
        
        task.write({'state': 'in_progress'})
        task.write({'state': 'submitted'})
        self.assertEqual(task.state, 'submitted')
        
        task.action_approve()
        self.assertEqual(task.state, 'approved')
        self.assertTrue(task.approved_by)
        self.assertTrue(task.approval_date)
    
    def test_next_report_date_calculation(self):
        """Test next report date calculation based on frequency."""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        start_date = date(2024, 1, 1)
        
        # Test quarterly
        next_date = self.compliance_profile.calculate_next_report_date(start_date)
        expected = start_date + relativedelta(months=3)
        self.assertEqual(next_date, expected)
    
    def test_compliance_checklist_parsing(self):
        """Test parsing of compliance checklist JSON."""
        import json
        
        checklist_data = [
            {'name': 'Item 1', 'completed': False},
            {'name': 'Item 2', 'completed': True},
        ]
        
        self.compliance_profile.write({
            'compliance_checklist': json.dumps(checklist_data)
        })
        
        items = self.compliance_profile.get_compliance_checklist_items()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['name'], 'Item 1')
    
    def test_generate_compliance_tasks_from_profile(self):
        """Test generating compliance tasks from profile."""
        import json
        
        # Set up checklist in profile
        checklist = [
            {
                'name': 'Financial Report Q1',
                'type': 'report',
                'level': 'contract',
                'priority': 'high',
                'deadline': '2024-04-15',
                'requires_document': True,
            },
            {
                'name': 'Procurement Plan Review',
                'type': 'review',
                'level': 'contract',
                'priority': 'normal',
                'deadline': '2024-03-01',
            },
        ]
        
        self.compliance_profile.write({
            'compliance_checklist': json.dumps(checklist)
        })
        
        # Generate tasks
        initial_count = len(self.contract.compliance_task_ids)
        self.contract.action_generate_compliance_tasks()
        
        # Verify tasks were created
        self.assertGreater(len(self.contract.compliance_task_ids), initial_count)
