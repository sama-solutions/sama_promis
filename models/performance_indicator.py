# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SamaPromisPerformanceIndicator(models.Model):
    _name = 'sama.promis.performance.indicator'
    _description = 'Performance Indicator'
    _order = 'sequence, name'

    name = fields.Char(string="Indicator Name", required=True)
    description = fields.Text(string="Description")
    project_id = fields.Many2one('project.project', string="Project",
                               required=True, ondelete='cascade')

    # Indicator Details
    indicator_type = fields.Selection([
        ('quantitative', 'Quantitative'),
        ('qualitative', 'Qualitative'),
        ('binary', 'Binary (Yes/No)'),
        ('percentage', 'Percentage'),
    ], string="Indicator Type", required=True, default='quantitative')

    unit_of_measure = fields.Char(string="Unit of Measure",
                                 help="e.g., people, kilometers, percentage, etc.")

    # Target and Current Values
    target_value = fields.Float(string="Target Value", digits=(12, 2))
    current_value = fields.Float(string="Current Value", digits=(12, 2),
                                compute='_compute_current_value', store=True)

    # Progress Tracking
    achievement_percentage = fields.Float(string="Achievement (%)",
                                        compute='_compute_achievement_percentage',
                                        store=True)

    # Dates
    baseline_date = fields.Date(string="Baseline Date")
    target_date = fields.Date(string="Target Date")
    last_update_date = fields.Date(string="Last Update",
                                 default=fields.Date.today)

    # Status
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('behind', 'Behind Schedule'),
        ('achieved', 'Achieved'),
    ], string="Status", compute='_compute_status', store=True)

    # Data Collection
    measurement_ids = fields.One2many('sama.promis.indicator.measurement',
                                    'indicator_id',
                                    string="Measurements")

    # Categorization
    category = fields.Selection([
        ('output', 'Output'),
        ('outcome', 'Outcome'),
        ('impact', 'Impact'),
        ('process', 'Process'),
    ], string="Indicator Category", required=True, default='output')

    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    # Constraints
    _sql_constraints = [
        ('positive_target', 'CHECK(target_value >= 0)',
         'Target value must be positive.'),
    ]

    @api.depends('measurement_ids', 'measurement_ids.value')
    def _compute_current_value(self):
        """Compute current value based on latest measurement"""
        for indicator in self:
            latest_measurement = indicator.measurement_ids.filtered(
                lambda m: m.measurement_date
            ).sorted('measurement_date', reverse=True)

            if latest_measurement:
                indicator.current_value = latest_measurement[0].value
            else:
                indicator.current_value = 0.0

    @api.depends('current_value', 'target_value')
    def _compute_achievement_percentage(self):
        """Calculate achievement percentage"""
        for indicator in self:
            if indicator.target_value != 0:
                indicator.achievement_percentage = (indicator.current_value / indicator.target_value) * 100
            else:
                indicator.achievement_percentage = 0.0

    @api.depends('achievement_percentage', 'target_date')
    def _compute_status(self):
        """Compute indicator status based on achievement and timeline"""
        for indicator in self:
            if indicator.achievement_percentage >= 100:
                indicator.status = 'achieved'
            elif indicator.achievement_percentage == 0:
                indicator.status = 'not_started'
            elif indicator.achievement_percentage >= 80:
                indicator.status = 'on_track'
            elif indicator.achievement_percentage >= 50:
                indicator.status = 'at_risk'
            else:
                indicator.status = 'behind'

    def action_add_measurement(self):
        """Open wizard to add new measurement"""
        return {
            'name': _('Add Measurement'),
            'type': 'ir.actions.act_window',
            'res_model': 'sama.promis.indicator.measurement',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_indicator_id': self.id,
                'default_measurement_date': fields.Date.today(),
            }
        }


class SamaPromisIndicatorMeasurement(models.Model):
    _name = 'sama.promis.indicator.measurement'
    _description = 'Indicator Measurement'
    _order = 'measurement_date desc'

    indicator_id = fields.Many2one('sama.promis.performance.indicator',
                                 string="Indicator",
                                 required=True, ondelete='cascade')

    measurement_date = fields.Date(string="Measurement Date",
                                 required=True, default=fields.Date.today)
    value = fields.Float(string="Measured Value", digits=(12, 2), required=True)

    # Qualitative assessment for non-quantitative indicators
    qualitative_assessment = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('satisfactory', 'Satisfactory'),
        ('needs_improvement', 'Needs Improvement'),
        ('poor', 'Poor'),
    ], string="Qualitative Assessment")

    notes = fields.Text(string="Notes")
    evidence_document = fields.Binary(string="Supporting Document")
    evidence_filename = fields.Char(string="Document Name")

    # Data source and verification
    data_source = fields.Char(string="Data Source")
    verified_by = fields.Many2one('res.users', string="Verified By")
    verification_date = fields.Date(string="Verification Date")

    @api.constrains('measurement_date', 'indicator_id')
    def _check_measurement_date(self):
        """Ensure measurement date is not in the future"""
        for measurement in self:
            if measurement.measurement_date > fields.Date.today():
                raise ValidationError(_("Measurement date cannot be in the future."))
