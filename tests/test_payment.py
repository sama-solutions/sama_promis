# -*- coding: utf-8 -*-

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta

@tagged('post_install', '-at_install')
class TestPaymentRequest(TransactionCase):
    """Test cases for SAMA PROMIS Payment Request"""

    def setUp(self):
        super(TestPaymentRequest, self).setUp()
        
        # Create test data
        self.test_project = self.env['project.project'].create({
            'name': 'Test Project',
            'project_type': 'operational_initiative',
        })
        
        self.test_contract = self.env['sama.promis.contract'].create({
            'name': 'Test Contract',
            'project_id': self.test_project.id,
            'total_amount': 10000.0,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        self.payment_model = self.env['sama.promis.payment.request']
        self.test_user = self.env.ref('base.user_demo')
        self.test_manager = self.env.ref('base.user_admin')

    def test_create_payment_request(self):
        """Test creating a payment request"""
        payment = self.payment_model.create({
            'project_id': self.test_project.id,
            'contract_id': self.test_contract.id,
            'amount': 1000.0,
        })
        
        self.assertEqual(payment.state, 'draft')
        self.assertEqual(payment.amount, 1000.0)
        self.assertTrue(payment.name.startswith('PR-'))

    def test_payment_workflow(self):
        """Test the complete payment workflow"""
        # Create payment request
        payment = self.payment_model.create({
            'project_id': self.test_project.id,
            'contract_id': self.test_contract.id,
            'amount': 1000.0,
        })
        
        # Submit payment
        payment.action_submit()
        self.assertEqual(payment.state, 'submitted')
        
        # Approve payment
        payment.action_approve()
        self.assertEqual(payment.state, 'approved')
        
        # Mark as paid
        payment.write({
            'state': 'paid',
            'payment_date': date.today(),
            'payment_reference': 'TEST123'
        })
        self.assertEqual(payment.state, 'paid')

    def test_payment_validation(self):
        """Test payment validations"""
        # Test zero amount
        with self.assertRaises(ValidationError):
            self.payment_model.create({
                'project_id': self.test_project.id,
                'contract_id': self.test_contract.id,
                'amount': 0.0,
            })
        
        # Test negative amount
        with self.assertRaises(ValidationError):
            self.payment_model.create({
                'project_id': self.test_project.id,
                'contract_id': self.test_contract.id,
                'amount': -100.0,
            })

    def test_security(self):
        """Test security rules"""
        # Create payment as admin
        payment = self.payment_model.create({
            'project_id': self.test_project.id,
            'contract_id': self.test_contract.id,
            'amount': 1000.0,
        })
        
        # Test user can only see their own payments
        payment_user = self.payment_model.with_user(self.test_user).create({
            'project_id': self.test_project.id,
            'contract_id': self.test_contract.id,
            'amount': 500.0,
            'user_id': self.test_user.id,
        })
        
        # Regular user should only see their payment
        payments = self.payment_model.with_user(self.test_user).search([])
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].id, payment_user.id)
        
        # Manager should see all payments
        payments = self.payment_model.with_user(self.test_manager).search([])
        self.assertGreaterEqual(len(payments), 2)
