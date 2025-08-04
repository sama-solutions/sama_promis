# -*- coding: utf-8 -*-
from odoo import models, fields

# Modele pour la ventilation des coûts
class ProjectCostBreakdown(models.Model):
    _name = 'project.cost.breakdown'
    _description = 'Ventilation du Coût par Composante'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    component_name = fields.Char(string='Nom de la Composante', required=True)
    estimated_cost = fields.Monetary(string='Coût Estimé', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id', string='Devise')
    description = fields.Text(string='Description')

# Modele pour les sources de financement
class ProjectFundingSource(models.Model):
    _name = 'project.funding.source'
    _description = 'Source de Financement du Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    source_name = fields.Char(string='Nom de la Source', required=True)
    amount = fields.Monetary(string='Montant', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id', string='Devise')
    percentage = fields.Float(string='Pourcentage (%)')

# Modele pour le plan de décaissement
class ProjectDisbursementPlan(models.Model):
    _name = 'project.disbursement.plan'
    _description = 'Plan de Décaissement Prévisionnel'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    year = fields.Char(string='Année', required=True) # Using Char for flexibility e.g., "2024-2025"
    planned_amount = fields.Monetary(string='Montant Prévu', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id', string='Devise')
    source_name = fields.Char(string='Source de Financement')

# Modele pour les textes juridiques
class ProjectLegalText(models.Model):
    _name = 'project.legal.text'
    _description = 'Texte Juridique Spécifique au Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    title = fields.Char(string='Titre du Texte', required=True)
    reference = fields.Char(string='Référence (Loi, Décret, etc.)')
    description = fields.Text(string='Description')

# Modele pour les conventions et accords
class ProjectAgreement(models.Model):
    _name = 'project.agreement'
    _description = 'Convention ou Accord lié au Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    agreement_type = fields.Selection([
        ('national', 'National'),
        ('international', 'International'),
        ('partnership', 'Partenariat'),
        ('other', 'Autre')
    ], string='Type d'Accord')
    title = fields.Char(string='Titre', required=True)
    reference = fields.Char(string='Référence')
    parties = fields.Char(string='Parties Prenantes')
    date_signed = fields.Date(string='Date de Signature')

# Modele pour les marchés publics
class ProjectPublicTender(models.Model):
    _name = 'project.public.tender'
    _description = 'Marché Public Associé au Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    name = fields.Char(string='Désignation du Marché', required=True)
    tender_type = fields.Selection([
        ('works', 'Travaux'),
        ('supplies', 'Fournitures'),
        ('services', 'Services')
    ], string='Nature du Marché')
    estimated_amount = fields.Monetary(string='Montant Estimé', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id', string='Devise')
    procedure_type = fields.Char(string='Type de Procédure') # e.g., Appel d'offres ouvert, restreint
    planned_start_date = fields.Date(string='Date de Démarrage Prévue')
    planned_end_date = fields.Date(string='Date de Fin Prévue')
    validation_organs = fields.Char(string='Organes de Validation (DCMP, ARMP)')
    specific_clauses = fields.Text(string='Clauses Spécifiques (Sociales, Environnementales)')
    litigation_mechanism = fields.Text(string='Mécanisme de Gestion des Litiges')
    plan_passation_marches_ref = fields.Char(string='Référence au PCPM')

# Modele pour les indicateurs de performance (KPI)
class ProjectKpi(models.Model):
    _name = 'project.kpi'
    _description = 'Indicateur de Performance du Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    kpi_type = fields.Selection([
        ('product', 'Produit'),
        ('result', 'Résultat'),
        ('impact', 'Impact')
    ], string='Type d'Indicateur', required=True)
    name = fields.Char(string='Nom de l'Indicateur', required=True)
    unit_of_measure = fields.Char(string='Unité de Mesure')
    target_value = fields.Float(string='Valeur Cible')
    current_value = fields.Float(string='Valeur Actuelle')
    frequency_collection = fields.Char(string='Fréquence de Collecte')
    last_update_date = fields.Date(string='Dernière Mise à Jour')

# Modele pour le plan d'évaluation
class ProjectEvaluationPlan(models.Model):
    _name = 'project.evaluation.plan'
    _description = 'Plan d'Évaluation du Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    evaluation_type = fields.Selection([
        ('mid_term', 'Mi-parcours'),
        ('final', 'Finale'),
        ('ex_post', 'Ex-post')
    ], string='Type d'Évaluation', required=True)
    planned_date = fields.Date(string='Date Prévue')
    responsible_entity = fields.Char(string='Entité Responsable')

# Modele pour les risques
class ProjectRisk(models.Model):
    _name = 'project.risk'
    _description = 'Risque Associé au Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    risk_type = fields.Selection([
        ('technical', 'Technique'),
        ('financial', 'Financier'),
        ('social', 'Social'),
        ('environmental', 'Environnemental'),
        ('governance', 'Gouvernance')
    ], string='Type de Risque')
    description = fields.Text(string='Description du Risque', required=True)
    impact_potential = fields.Selection([('1', 'Faible'), ('2', 'Modéré'), ('3', 'Élevé')], string='Impact Potentiel')
    probability = fields.Selection([('1', 'Faible'), ('2', 'Moyenne'), ('3', 'Élevée')], string='Probabilité')
    mitigation_measure = fields.Text(string='Mesure d'Atténuation')
    responsible_person = fields.Char(string='Responsable')

# Modele pour le PGES
class ProjectPges(models.Model):
    _name = 'project.pges'
    _description = 'Plan de Gestion Environnementale et Sociale (PGES)'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    document_name = fields.Char(string='Nom du Document', required=True)
    document_attachment = fields.Binary(string='Fichier PGES', attachment=True)
    validation_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('in_review', 'En revue')
    ], string='Statut de Validation')

# Modele pour les structures de coordination
class ProjectCoordinationStructure(models.Model):
    _name = 'project.coordination.structure'
    _description = 'Structure de Coordination du Projet'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    name = fields.Char(string='Nom de la Structure', required=True)
    role = fields.Text(string='Rôle et Responsabilités')

# Modele pour les rôles et responsabilités
class ProjectRoleResponsibility(models.Model):
    _name = 'project.role.responsibility'
    _description = 'Rôle et Responsabilité'

    project_id = fields.Many2one('government.project', string='Projet Gouvernemental', required=True, ondelete='cascade')
    name = fields.Char(string='Acteur/Entité', required=True)
    role_description = fields.Text(string='Description du Rôle')
