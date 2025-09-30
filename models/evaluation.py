# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SamaPromisProjectEvaluation(models.Model):
    _name = 'sama.promis.project.evaluation'
    _description = 'Project Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Reference", compute='_compute_name')
    project_id = fields.Many2one('sama.promis.project', string="Project", required=True, ondelete='cascade')
    call_id = fields.Many2one('sama.promis.call.proposal', string="Call for Proposal", required=True, ondelete='cascade')
    evaluator_id = fields.Many2one('res.users', string="Evaluator", required=True, default=lambda self: self.env.user)
    
    # Evaluation Details
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string="Status", default='draft', tracking=True)
    
    evaluation_date = fields.Datetime(string="Evaluation Date", default=fields.Datetime.now)
    score = fields.Float(string="Total Score", compute='_compute_score', store=True, digits=(5, 2))
    notes = fields.Text(string="Evaluation Notes")
    
    # Criteria Scores
    criterion_ids = fields.One2many('sama.promis.evaluation.score', 'evaluation_id', string="Criteria Scores")
    
    # Constraints
    _sql_constraints = [
        ('unique_evaluator_per_project', 
         'UNIQUE(project_id, evaluator_id, call_id)',
         'Each evaluator can only evaluate a project once per call.')
    ]
    
    @api.depends('project_id', 'call_id', 'evaluator_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.project_id.name} - {rec.evaluator_id.name}"
    
    @api.depends('criterion_ids.score')
    def _compute_score(self):
        for rec in self:
            rec.score = sum(rec.criterion_ids.mapped('score'))
    
    def action_start_evaluation(self):
        """Start the evaluation process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft evaluations can be started."))
        
        # Create evaluation criteria lines if they don't exist
        if not self.criterion_ids:
            self._create_criteria_lines()
        
        self.write({'state': 'in_progress'})
    
    def action_complete_evaluation(self):
        """Mark evaluation as complete"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Only evaluations in progress can be completed."))
        
        if not self.criterion_ids:
            raise UserError(_("Please complete the evaluation criteria before submitting."))
        
        self.write({
            'state': 'completed',
            'evaluation_date': fields.Datetime.now()
        })
        
        # Notify project team
        self._notify_completion()
    
    def _create_criteria_lines(self):
        """Create evaluation criteria lines from the call for proposal"""
        self.ensure_one()
        if not self.call_id.evaluation_criteria_ids:
            raise UserError(_("No evaluation criteria defined for this call."))
        
        lines = []
        for criteria in self.call_id.evaluation_criteria_ids:
            lines.append((0, 0, {
                'criteria_id': criteria.id,
                'max_score': criteria.weight,
                'evaluation_id': self.id,
            }))
        
        self.write({'criterion_ids': lines})
    
    def _notify_completion(self):
        """Notify relevant users about evaluation completion"""
        # Implementation for sending notifications
        pass


class SamaPromisEvaluationScore(models.Model):
    _name = 'sama.promis.evaluation.score'
    _description = 'Evaluation Score'
    
    evaluation_id = fields.Many2one('sama.promis.project.evaluation', string="Evaluation", ondelete='cascade')
    criteria_id = fields.Many2one('sama.promis.evaluation.criteria', string="Criteria", required=True, ondelete='restrict')
    
    # Evaluation Fields
    score = fields.Float(string="Score", digits=(5, 2), default=0.0)
    max_score = fields.Float(string="Max Score", digits=(5, 2))
    notes = fields.Text(string="Comments")
    
    # Constraints
    _sql_constraints = [
        ('score_range', 'CHECK(score >= 0 AND score <= max_score)',
         'Score must be between 0 and the maximum score.')
    ]
    
    @api.onchange('score')
    def _onchange_score(self):
        """Ensure score doesn't exceed max score"""
        if self.score > self.max_score:
            self.score = self.max_score
            return {
                'warning': {
                    'title': _("Invalid Score"),
                    'message': _("Score cannot exceed the maximum score of %.2f") % self.max_score,
                }
            }
