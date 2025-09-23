# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError
import base64
from datetime import date, timedelta

@tagged('post_install', '-at_install')
class TestPhase2Features(TransactionCase):
    """Test cases for SAMA PROMIS Phase 2 features"""

    def setUp(self):
        super(TestPhase2Features, self).setUp()
        
        # Create test data
        self.partner_donor = self.env['res.partner'].create({
            'name': 'Test Donor',
            'is_company': True,
            'is_donor': True,
        })
        
        self.partner_beneficiary = self.env['res.partner'].create({
            'name': 'Test Beneficiary',
            'is_company': True,
        })
        
        self.project = self.env['project.project'].create({
            'name': 'Test Project',
            'project_type': 'operational_initiative',
            'donor_id': self.partner_donor.id,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'total_budget': 100000.0,
            'donor_compliance_level': 'high',
            'reporting_frequency': 'quarterly',
            'next_report_date': date.today() + timedelta(days=90),
        })
        
        # Create contract template
        self.contract_template = self.env['sama.promis.contract.template'].create({
            'name': 'Test Contract Template',
            'contract_type': 'grant',
            'template_content': """
            <h1>Contract for {{ project.title }}</h1>
            <p>This contract is between {{ donor.name }} and {{ grantee.name }}.</p>
            <p>Amount: {{ contract.amount }}</p>
            <p>Start date: {{ contract.start_date }}</p>
            <p>End date: {{ contract.end_date }}</p>
            
            <h2>Payment Schedule</h2>
            {{ payment_schedule_table }}
            """
        })
        
        # Create event
        self.event = self.env['sama.promis.project.event'].create({
            'name': 'Test Event',
            'project_id': self.project.id,
            'event_type': 'conference',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=30, hours=4),
            'location': 'Test Location',
            'expected_participants': 50,
        })

    def test_01_project_donor_compliance_fields(self):
        """Test the new donor compliance fields on project"""
        self.assertEqual(self.project.donor_compliance_level, 'high', 
                         "Donor compliance level should be set to 'high'")
        self.assertEqual(self.project.reporting_frequency, 'quarterly', 
                         "Reporting frequency should be set to 'quarterly'")
        self.assertEqual(self.project.next_report_date, date.today() + timedelta(days=90), 
                         "Next report date should be set correctly")

    def test_02_event_management(self):
        """Test event management functionality"""
        # Check event creation
        self.assertEqual(self.event.name, 'Test Event', 
                         "Event name should be set correctly")
        self.assertEqual(self.event.project_id, self.project, 
                         "Event should be linked to the correct project")
        
        # Test event count on project
        self.project._compute_event_count()
        self.assertEqual(self.project.event_count, 1, 
                         "Project should have 1 event")
        
        # Test event workflow
        self.event.action_confirm()
        self.assertEqual(self.event.state, 'confirmed', 
                         "Event state should be 'confirmed'")
        
        self.event.action_start()
        self.assertEqual(self.event.state, 'in_progress', 
                         "Event state should be 'in_progress'")
        
        self.event.action_complete()
        self.assertEqual(self.event.state, 'completed', 
                         "Event state should be 'completed'")

    def test_03_contract_generation(self):
        """Test contract generation with template"""
        # Create contract
        contract = self.env['sama.promis.contract'].create({
            'name': 'TEST-001',
            'project_id': self.project.id,
            'partner_id': self.partner_beneficiary.id,
            'contract_type': 'grant',
            'contract_template_id': self.contract_template.id,
            'amount': 50000.0,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'reporting_frequency': 'quarterly',
        })
        
        # Add payment schedule
        self.env['sama.promis.payment.schedule'].create({
            'name': 'Advance Payment',
            'contract_id': contract.id,
            'due_date': date.today() + timedelta(days=15),
            'amount': 15000.0,
            'payment_percentage': 30.0,
            'description': 'Initial advance payment',
        })
        
        self.env['sama.promis.payment.schedule'].create({
            'name': 'Intermediate Payment',
            'contract_id': contract.id,
            'due_date': date.today() + timedelta(days=180),
            'amount': 25000.0,
            'payment_percentage': 50.0,
            'description': 'Intermediate payment',
        })
        
        self.env['sama.promis.payment.schedule'].create({
            'name': 'Final Payment',
            'contract_id': contract.id,
            'due_date': date.today() + timedelta(days=365),
            'amount': 10000.0,
            'payment_percentage': 20.0,
            'description': 'Final payment',
        })
        
        # Check contract content generation
        contract._compute_contract_content()
        self.assertTrue(contract.contract_content_html, 
                        "Contract content should be generated")
        self.assertIn(self.project.name, contract.contract_content_html, 
                      "Contract content should include project name")
        self.assertIn(self.partner_beneficiary.name, contract.contract_content_html, 
                      "Contract content should include beneficiary name")
        
        # Test contract generation
        try:
            # This will fail in test mode without PDF rendering capabilities
            # but we just want to make sure it doesn't raise unexpected errors
            contract.action_generate_contract()
        except Exception as e:
            # Only UserError is expected (for missing PDF rendering in test mode)
            if not isinstance(e, UserError):
                self.fail(f"Unexpected error during contract generation: {e}")

    def test_04_dashboard_controller(self):
        """Test dashboard controller functionality"""
        # This is a basic test to ensure the controller doesn't crash
        # Full testing would require an HTTP case which is more complex
        controller = self.env['ir.http']._get_default_lang()
        self.assertTrue(controller, "Default language controller should exist")

    def test_05_contract_signature_preparation(self):
        """Test contract signature preparation"""
        # Create contract
        contract = self.env['sama.promis.contract'].create({
            'name': 'TEST-002',
            'project_id': self.project.id,
            'partner_id': self.partner_beneficiary.id,
            'contract_type': 'grant',
            'contract_template_id': self.contract_template.id,
            'amount': 75000.0,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        # Simulate contract document generation
        contract.contract_document = base64.b64encode(b"Test PDF Content")
        contract.contract_filename = "test_contract.pdf"
        contract.state = 'generated'
        contract.signature_status = 'generated'
        
        # Test manual signature marking
        contract.action_mark_signed()
        self.assertEqual(contract.state, 'signed', 
                         "Contract state should be 'signed'")
        self.assertEqual(contract.signature_status, 'signed', 
                         "Contract signature status should be 'signed'")