from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectPublicProject(models.Model):
    _name = 'project.public.project'
    _description = 'Fiche Projet Public'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Titre du Projet', required=True, tracking=True, help="Nom complet et clair du projet.")
    code = fields.Char(string='Code Projet Unique', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), help="Code alphanumérique unique pour le projet.")
    description_sommaire = fields.Text(string='Description Sommaire', help="Résumé des objectifs, activités et résultats attendus. (LOLF Art. 13, Directives UEMOA)")
    secteur_intervention = fields.Many2one('project.public.sector', string='Secteur d\'Intervention', required=True, tracking=True, help="Secteur principal dans lequel le projet est classifié.")
    maitre_ouvrage_id = fields.Many2one('res.partner', string='Maître d\'Ouvrage', required=True, help="Entité publique responsable. (LOLF Art. 13, RGCP Art. 16)")
    maitre_ouvrage_delegue_id = fields.Many2one('res.partner', string='Maître d\'Ouvrage Délégué', help="Entité à qui la maîtrise d'ouvrage est déléguée. (CMP Art. 8)")
    date_debut_previsionnelle = fields.Date(string='Date Début Prévisionnelle', required=True)
    date_fin_previsionnelle = fields.Date(string='Date Fin Prévisionnelle', required=True)
    duree_en_mois = fields.Integer(string='Durée (mois)', compute='_compute_duree_en_mois', store=True)

    @api.depends('date_debut_previsionnelle', 'date_fin_previsionnelle')
    def _compute_duree_en_mois(self):
        for rec in self:
            if rec.date_debut_previsionnelle and rec.date_fin_previsionnelle:
                delta = rec.date_fin_previsionnelle - rec.date_debut_previsionnelle
                rec.duree_en_mois = round(delta.days / 30.44)
            else:
                rec.duree_en_mois = 0

    region_ids = fields.Many2many('res.country.state', 'project_region_rel', 'project_id', 'state_id', string='Région(s)', domain=[('country_id.code', '=', 'SN')], help="Région(s) d'implantation du projet. (LOLF Art. 13, CGCT Art. 188)")
    departement_ids = fields.Many2many('project.public.location.departement', 'project_departement_rel', 'project_id', 'departement_id', string='Département(s)', help="Département(s) d'implantation.")
    commune_ids = fields.Many2many('project.public.location.commune', 'project_commune_rel', 'project_id', 'commune_id', string='Commune(s)', help="Commune(s) d'implantation.")
    coordonnees_gps_principales = fields.Char(string='Coordonnées GPS Principales', help="Ex: Latitude, Longitude")

    entite_responsable_principale_id = fields.Many2one('res.partner', string='Entité Responsable Principale', required=True, help="Ministère/Agence/CT ayant la tutelle. (LOLF Art. 13, RGCP Art. 16, CGCT)")
    responsable_projet_id = fields.Many2one('res.users', string='Responsable Projet Odoo', help="Utilisateur Odoo en charge du projet.")
    contact_email = fields.Char(string='Email Contact', related='responsable_projet_id.email', readonly=True)
    contact_phone = fields.Char(string='Téléphone Contact', related='responsable_projet_id.phone', readonly=True)
    partenaires_ids = fields.One2many('project.public.partner', 'project_id', string='Partenaires (Techniques et Financiers)', help="Liste des partenaires et leurs contributions.")

    base_legale_creation = fields.Text(string='Base Légale de Création', help="Loi, Décret, Arrêté de création du projet. (LOLF Art. 13, RGCP Art. 16)")
    references_politiques_publiques = fields.Many2many('project.public.policy', 'project_policy_rel', 'project_id', 'policy_id', string='Références Politiques Publiques', help="Ex: PSE, Stratégies sectorielles.")
    autres_textes_reglementaires = fields.Text(string='Autres Textes Réglementaires Applicables', help="Références à d'autres lois ou décrets pertinents (ex: Code de l'Environnement).")

    cout_total_estime = fields.Monetary(string='Coût Total Estimé', currency_field='currency_id', required=True, tracking=True, help="Montant total en FCFA. (LOLF Art. 13, 14, 15)")
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id, required=True)
    repartition_annuelle_ids = fields.One2many('project.public.budget.annual', 'project_id', string='Répartition Prévisionnelle Annuelle', help="Détail du budget par année. (LOLF Art. 14, DGB, CDMT)")
    sources_financement_ids = fields.One2many('project.public.finance.source', 'project_id', string='Sources de Financement', help="Détail des contributeurs et montants. (LOLF Art. 13, 14, RGCP Art. 25-27)")
    mode_gestion_budgetaire = fields.Selection([
        ('regie', 'Régie'),
        ('ordonnancement', 'Ordonnancement'),
        ('caisse_avance', 'Caisse d\'Avance'),
        ('autre', 'Autre')
    ], string='Mode de Gestion Budgétaire', default='ordonnancement')

    marches_publics_ids = fields.One2many('project.public.procurement', 'project_id', string='Marchés Publics Prévus', help="Liste détaillée des marchés liés au projet.")
    exigences_particulieres_cmp = fields.Text(string='Exigences Particulières CMP', help="Clauses sociales, environnementales, préférence nationale, etc.")

    indicateurs_performance_ids = fields.One2many('project.public.indicator', 'project_id', string='Indicateurs de Performance', help="Mesures quantitatives et qualitatives. (LOLF Art. 13, Directives UEMOA)")
    methodologie_suivi_evaluation = fields.Text(string='Méthodologie Suivi-Évaluation', help="Outils et méthodes de suivi. (IGE, DGB)")
    frequence_rapports_suivi = fields.Selection([
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel'),
        ('annuel', 'Annuel')
    ], string='Fréquence Rapports Suivi', default='trimestriel', required=True, help="Fréquence des rapports d'avancement. (LOLF Art. 13, DGB)")
    rapports_evaluation_prevus = fields.Char(string='Rapports Évaluation Prévus', help="Ex: Évaluation à mi-parcours, évaluation finale.")

    analyse_risques_ids = fields.One2many('project.public.risk', 'project_id', string='Analyse des Risques Majeurs', help="Identification et mesures d'atténuation. (PTF, Code de l'Environnement)")
    eies_requise = fields.Selection([('oui', 'Oui'), ('non', 'Non'), ('n/a', 'N/A')], string='EIES Requise ?', default='n/a', required=True, help="Étude d'Impact Environnemental et Social. (Loi n°2001-01, Décret n°2001-834)")
    date_validation_eies = fields.Date(string='Date Validation EIES')
    reference_eies = fields.Char(string='Référence Rapport EIES')
    pges_existe = fields.Boolean(string='Plan de Gestion Environnemental et Social (PGES) Existe ?')
    impact_social_analyse = fields.Text(string='Analyse Impact Social', help="Description des impacts sociaux potentiels et mesures d'atténuation.")

    publication_prevue = fields.Boolean(string='Publication des informations prévue ?', default=True, help="Les informations du projet seront-elles publiées ? (CMP Art. 21, 22, Directive UEMOA Transparence)")
    plateforme_publication = fields.Char(string='Plateforme de Publication', help="Ex: Site web du Ministère, Portail e-procurement, Portail Open Data.")
    type_informations_publiees = fields.Many2many('project.public.info.type', 'project_info_type_rel', 'project_id', 'info_type_id', string='Types d\'informations publiées', help="Ex: Fiche projet, rapports, résultats appels d'offres.")
    mecanisme_plainte_existe = fields.Boolean(string='Mécanisme de Plaintes/Recours Existant ?', help="Existe-t-il un mécanisme pour les réclamations ? (CMP Art. 136, ARMP)")
    details_mecanisme_plainte = fields.Text(string='Détails Mécanisme Plaintes/Recours', help="Ex: Comité de recours des marchés publics, points focaux.")
    audits_controles_prevus = fields.Char(string='Audits/Contrôles Prévus', help="Ex: Audit Cour des Comptes, IGE, PTF.")

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('project.public.project.sequence') or _('New')
        return super(ProjectPublicProject, self).create(vals)

    @api.constrains('date_debut_previsionnelle', 'date_fin_previsionnelle')
    def _check_dates(self):
        for rec in self:
            if rec.date_debut_previsionnelle and rec.date_fin_previsionnelle and rec.date_fin_previsionnelle < rec.date_debut_previsionnelle:
                raise ValidationError(_("La date de fin prévisionnelle ne peut pas être antérieure à la date de début prévisionnelle."))

