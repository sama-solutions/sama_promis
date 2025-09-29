# -*- coding: utf-8 -*-
"""Tests liés aux QR codes générés pour les projets."""

from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged

try:
    import qrcode  # noqa: F401
    QRCODE_AVAILABLE = True
except ImportError:  # pragma: no cover - environment without qrcode lib
    QRCODE_AVAILABLE = False


@tagged('post_install', '-at_install')
class TestProjectQRCodes(TransactionCase):
    """Vérifie la génération des données QR Code pour les projets."""

    def setUp(self):
        super().setUp()
        self.env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://test.example')
        self.partner = self.env['res.partner'].create({
            'name': 'QR Partner',
        })

    def test_qr_code_fields_are_computed(self):
        """Les champs QR Code doivent être calculés lors de la création du projet."""
        project = self.env['sama.promis.project'].create({
            'name': 'QR Enabled Project',
            'project_type': 'education',
            'partner_id': self.partner.id,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
        })

        expected_path = f"/promispublic/project/{project.id}"
        self.assertTrue(project.qr_code_data, "Le champ qr_code_data doit être renseigné")
        self.assertTrue(project.qr_code_data.startswith('https://test.example'))
        self.assertIn(expected_path, project.qr_code_data)
        self.assertEqual(project.qr_code_url, project.qr_code_data)

        if QRCODE_AVAILABLE:
            self.assertTrue(project.qr_code_image, "L'image QR doit être générée lorsque qrcode est disponible")
        else:
            self.assertFalse(project.qr_code_image, "L'image QR doit être vide sans dépendance qrcode")
