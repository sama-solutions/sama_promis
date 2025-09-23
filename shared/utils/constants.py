# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Constants
=======================

Constantes partagées pour tous les micromodules SAMA PROMIS.
"""

# États des projets
PROJECT_STATES = [
    ('draft', 'Brouillon'),
    ('submitted', 'Soumis'),
    ('under_review', 'En Révision'),
    ('approved', 'Approuvé'),
    ('in_progress', 'En Cours'),
    ('suspended', 'Suspendu'),
    ('completed', 'Terminé'),
    ('cancelled', 'Annulé')
]

# États des appels à propositions
CALL_STATES = [
    ('draft', 'Brouillon'),
    ('published', 'Publié'),
    ('submission_open', 'Soumissions Ouvertes'),
    ('submission_closed', 'Soumissions Fermées'),
    ('under_evaluation', 'En Évaluation'),
    ('evaluation_completed', 'Évaluation Terminée'),
    ('closed', 'Clôturé')
]

# États des contrats
CONTRACT_STATES = [
    ('draft', 'Brouillon'),
    ('generated', 'Généré'),
    ('sent_for_signature', 'Envoyé pour Signature'),
    ('partially_signed', 'Partiellement Signé'),
    ('fully_signed', 'Entièrement Signé'),
    ('active', 'Actif'),
    ('expired', 'Expiré'),
    ('terminated', 'Résilié')
]

# États des paiements
PAYMENT_STATES = [
    ('draft', 'Brouillon'),
    ('requested', 'Demandé'),
    ('under_review', 'En Révision'),
    ('approved', 'Approuvé'),
    ('processed', 'Traité'),
    ('paid', 'Payé'),
    ('rejected', 'Rejeté')
]

# États des évaluations
EVALUATION_STATES = [
    ('draft', 'Brouillon'),
    ('in_progress', 'En Cours'),
    ('completed', 'Terminée'),
    ('validated', 'Validée'),
    ('published', 'Publiée')
]

# Types de projets
PROJECT_TYPES = [
    ('operational_call', 'Opérationnel (Appel à Propositions)'),
    ('operational_initiative', 'Opérationnel (Initiative du Programme)'),
    ('administrative', 'Administratif')
]

# Priorités
PRIORITIES = [
    ('low', 'Faible'),
    ('medium', 'Moyenne'),
    ('high', 'Élevée'),
    ('urgent', 'Urgente')
]

# Niveaux de risque
RISK_LEVELS = [
    ('low', 'Faible'),
    ('medium', 'Moyen'),
    ('high', 'Élevé'),
    ('critical', 'Critique')
]

# Types de partenaires
PARTNER_TYPES = [
    ('donor', 'Bailleur de Fonds'),
    ('beneficiary', 'Bénéficiaire'),
    ('implementing_partner', 'Partenaire de Mise en Œuvre'),
    ('government', 'Gouvernement'),
    ('ngo', 'ONG'),
    ('private_sector', 'Secteur Privé'),
    ('academic', 'Académique'),
    ('citizen', 'Citoyen')
]

# Devises principales
CURRENCIES = [
    ('XOF', 'Franc CFA (XOF)'),
    ('EUR', 'Euro (EUR)'),
    ('USD', 'Dollar US (USD)'),
    ('GBP', 'Livre Sterling (GBP)')
]

# Langues supportées
LANGUAGES = [
    ('fr_FR', 'Français'),
    ('en_US', 'English'),
    ('ar_SA', 'العربية'),
    ('wo_SN', 'Wolof')
]

# URLs de base
BASE_URLS = {
    'public_dashboard': '/promispublic',
    'citizen_portal': '/promispublic/citizen',
    'api_base': '/api/v1/sama_promis',
    'qr_base': 'https://sama-promis.sn'
}

# Tailles de pagination
PAGINATION_SIZES = {
    'small': 5,
    'medium': 10,
    'large': 20,
    'xlarge': 50
}

# Formats de date
DATE_FORMATS = {
    'short': '%d/%m/%Y',
    'long': '%d %B %Y',
    'datetime': '%d/%m/%Y %H:%M',
    'iso': '%Y-%m-%d'
}

# Couleurs du thème
THEME_COLORS = {
    'primary': '#1e3a8a',      # Bleu institutionnel
    'secondary': '#059669',     # Vert SAMA
    'success': '#10b981',       # Vert succès
    'warning': '#f59e0b',       # Orange avertissement
    'danger': '#ef4444',        # Rouge erreur
    'info': '#3b82f6',          # Bleu information
    'light': '#f8fafc',         # Gris clair
    'dark': '#1f2937'           # Gris foncé
}