# SAMA PROMIS - Centre de Formation et Certification

## Vue d'ensemble

Bienvenue dans le Centre de Formation et Certification SAMA PROMIS. Ce site web statique fournit une formation complète et une certification officielle pour tous les utilisateurs du système SAMA PROMIS.

## Structure du Site

```
/docs/training/
├── index.html                          # Page d'accueil
├── register.html                       # Inscription
├── certification/
│   └── index.html                      # Centre de certification
├── roles/                              # Formations par rôle
│   ├── administrator/
│   │   ├── user-level.html
│   │   └── trainer-level.html
│   ├── project-manager/
│   │   ├── user-level.html
│   │   └── trainer-level.html
│   ├── donor/
│   │   └── user-level.html
│   ├── beneficiary/
│   │   └── user-level.html
│   ├── compliance-officer/
│   │   └── user-level.html
│   ├── procurement-officer/
│   │   └── user-level.html
│   ├── portal-user/
│   │   └── user-level.html
│   └── citizen/
│       └── user-level.html
├── resources/
│   ├── index.html                      # Ressources téléchargeables
│   └── files/                          # Fichiers PDF, vidéos, etc.
└── assets/
    ├── css/
    │   └── training-main.css           # Styles principaux
    ├── js/
    │   ├── training-core.js            # Fonctionnalités de base
    │   ├── quiz-system.js              # Système de quiz
    │   └── certificate-generator.js    # Générateur de certificats
    ├── images/                         # Images et icônes
    └── data/
        └── quizzes/                    # Données des quiz (JSON)
```

## Rôles et Formations

### 1. Administrateur Système
- **Niveau Utilisateur** (8h): Installation, configuration, gestion des utilisateurs, sécurité, maintenance
- **Niveau Formateur** (12h): Pédagogie, méthodologie d'enseignement, ressources pédagogiques

### 2. Chef de Projet
- **Niveau Utilisateur** (10h): Gestion de projets, budget multi-sources, passation de marchés, conformité
- **Niveau Formateur** (14h): Enseigner la gestion de projet, cas pratiques, évaluation

### 3. Bailleur de Fonds
- **Niveau Utilisateur** (6h): Portail public, profils de conformité, suivi des projets, rapports

### 4. Bénéficiaire/Partenaire
- **Niveau Utilisateur** (8h): Portail requérant, suivi des projets, propositions, contrats, conformité

### 5. Responsable Conformité
- **Niveau Utilisateur** (8h): Gestion des tâches de conformité, profils de conformité, rapportage

### 6. Responsable Passation de Marchés
- **Niveau Utilisateur** (8h): Plans de passation, appels d'offres, suivi de l'exécution

### 7. Utilisateur Portail (Requérant)
- **Niveau Utilisateur** (4h): Navigation du portail, suivi des interactions, documents

### 8. Citoyen (Portail Public)
- **Niveau Utilisateur** (2h): Navigation du portail public, consultation des données, export

## Certification

### Niveaux de Certification

**Certification Utilisateur:**
- Compléter tous les modules de formation
- Réussir les quiz de chaque module (80%)
- Réussir l'examen final (80%)
- Validité: 2 ans

**Certification Formateur:**
- Avoir la certification utilisateur
- Compléter les modules formateur
- Réussir l'examen formateur (85%)
- Soumettre une démonstration d'enseignement
- Validité: 3 ans

### Processus de Certification

1. **Inscription**: Créer un compte sur le site de formation
2. **Formation**: Suivre les modules de votre rôle
3. **Évaluation**: Passer les quiz et l'examen final
4. **Certification**: Recevoir votre certificat officiel
5. **Renouvellement**: Renouveler avant expiration

## Fonctionnalités Techniques

### Technologies Utilisées
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5 (responsive framework)
- Chart.js (visualisations)
- jsPDF (génération de certificats)
- QRCode.js (codes QR)
- LocalStorage (persistance des données)

### Suivi de Progression
La progression est sauvegardée localement dans le navigateur (localStorage). Les données incluent:
- Modules complétés
- Scores des quiz
- Temps passé
- Certificats obtenus

### Système de Quiz
- Questions à choix multiples
- Questions vrai/faux
- Questions à choix multiples (plusieurs réponses)
- Questions à compléter
- Minuteur
- Feedback immédiat
- Explications détaillées

### Génération de Certificats
- Certificats PDF téléchargeables
- QR code pour vérification
- Numéro unique de certificat
- Signatures officielles
- Imprimables

## Installation et Déploiement

### Prérequis
- Serveur web (Apache, Nginx, ou serveur de développement)
- Navigateur moderne (Chrome, Firefox, Safari, Edge)

### Installation Locale

```bash
# Cloner le dépôt
git clone <repository_url>
cd sama_promis/docs/training

# Lancer un serveur local (Python)
python3 -m http.server 8000

# Ou avec Node.js
npx http-server -p 8000

# Accéder au site
open http://localhost:8000
```

## Ouverture en Mode Local (file://)

### Problème des Chemins Relatifs

Lorsque vous ouvrez les fichiers HTML directement depuis votre système de fichiers (double-clic sur un fichier .html), le navigateur utilise le protocole `file://` au lieu de `http://`. Cela peut causer des problèmes avec les chemins relatifs.

### Solution Automatique

Le site de formation SAMA PROMIS inclut un **résolveur de chemins automatique** (`path-resolver.js`) qui détecte le mode `file://` et corrige automatiquement tous les liens.

**Aucune action requise de votre part** - ouvrez simplement n'importe quel fichier HTML et la navigation fonctionnera correctement.

### Comment Ouvrir le Site

**Option 1: Ouverture Directe (Recommandée pour consultation rapide)**

1. Naviguez vers `/docs/training/` dans votre explorateur de fichiers
2. Double-cliquez sur `index.html`
3. Le site s'ouvre dans votre navigateur par défaut
4. Tous les liens fonctionnent automatiquement grâce au path resolver

**Option 2: Serveur Web Local (Recommandée pour développement)**

Utilisez un serveur web local pour une expérience optimale:

```bash
# Avec Python 3
cd /path/to/sama_promis/docs/training
python3 -m http.server 8000

# Avec Node.js
cd /path/to/sama_promis/docs/training
npx http-server -p 8000

# Avec PHP
cd /path/to/sama_promis/docs/training
php -S localhost:8000
```

Puis ouvrez: `http://localhost:8000`

**Option 3: Extension VSCode Live Server**

1. Installez l'extension "Live Server" dans VSCode
2. Ouvrez le dossier `/docs/training/` dans VSCode
3. Clic droit sur `index.html` → "Open with Live Server"
4. Le site s'ouvre automatiquement dans votre navigateur

### Vérification du Fonctionnement

Pour vérifier que le path resolver fonctionne:

1. Ouvrez la console du navigateur (F12)
2. Vous devriez voir le message: `"File protocol detected, enabling path resolution"`
3. Puis: `"All paths resolved for file:// mode"`
4. Tous les liens devraient fonctionner correctement

### Dépannage

**Problème: Les CSS ne se chargent pas**
- **Cause**: Le path resolver n'a pas pu se charger
- **Solution**: Vérifiez que `assets/js/path-resolver.js` existe et est accessible

**Problème: Les liens ne fonctionnent pas**
- **Cause**: Restrictions de sécurité du navigateur
- **Solution**: Utilisez un serveur web local (Option 2 ou 3 ci-dessus)

**Problème: Erreur CORS dans la console**
- **Cause**: Certains navigateurs bloquent les requêtes file:// par sécurité
- **Solution**: Utilisez Chrome avec le flag `--allow-file-access-from-files` OU utilisez un serveur web local

### Navigateurs Recommandés

**Pour mode file://**
- ✅ Chrome/Chromium (meilleur support)
- ✅ Firefox (bon support)
- ⚠️ Safari (support limité)
- ⚠️ Edge (support limité)

**Pour mode http:// (serveur local)**
- ✅ Tous les navigateurs modernes

### Notes Techniques

**Comment fonctionne le path resolver:**

1. Détecte si `window.location.protocol === 'file:'`
2. Calcule le chemin absolu vers `/docs/training/`
3. Parcourt tous les éléments HTML (`<a>`, `<link>`, `<script>`, `<img>`)
4. Convertit les chemins relatifs en chemins absolus
5. Met à jour les attributs `href` et `src`

**Exemple de conversion:**
```
Fichier: file:///path/to/docs/training/roles/administrator/user-level.html
Lien original: href="../../assets/css/training-main.css"
Lien résolu: href="file:///path/to/docs/training/assets/css/training-main.css"
```

### Recommandation Finale

**Pour une utilisation occasionnelle:** Ouvrez directement les fichiers HTML (Option 1)

**Pour le développement ou la formation:** Utilisez un serveur web local (Option 2 ou 3)

**Pour la production:** Déployez sur un serveur web (voir section Déploiement)

### Déploiement en Production

1. **Hébergement Statique:**
   - GitHub Pages
   - Netlify
   - Vercel
   - AWS S3 + CloudFront

2. **Configuration:**
   - Configurer HTTPS
   - Configurer le domaine personnalisé
   - Activer la compression GZIP
   - Configurer le cache

3. **Optimisation:**
   - Minifier CSS/JS
   - Optimiser les images
   - Activer le lazy loading
   - Configurer le CDN

## Maintenance et Mises à Jour

### Ajouter un Nouveau Module

1. Créer le fichier HTML dans le répertoire approprié
2. Ajouter le contenu du module (leçons, quiz)
3. Créer les fichiers de quiz JSON
4. Mettre à jour la navigation
5. Tester la progression

### Ajouter un Nouveau Quiz

1. Créer un fichier JSON dans `/assets/data/quizzes/`
2. Définir les questions et réponses
3. Référencer le quiz dans la page HTML
4. Tester le quiz

### Mettre à Jour les Ressources

1. Ajouter les fichiers dans `/resources/files/`
2. Mettre à jour le fichier de métadonnées
3. Mettre à jour la page resources/index.html
4. Tester les téléchargements

## Structure des Données

### Format de Quiz (JSON)

```json
{
  "quizId": "admin-user-module1",
  "title": "Module 1: Installation et Configuration",
  "description": "Test your knowledge...",
  "timeLimit": 20,
  "passingScore": 80,
  "questions": [
    {
      "id": 1,
      "type": "multiple-choice",
      "question": "Question text?",
      "options": [
        { "id": "a", "text": "Option A", "correct": false },
        { "id": "b", "text": "Option B", "correct": true }
      ],
      "explanation": "Explanation text",
      "points": 2
    }
  ]
}
```

### Format de Données Utilisateur (LocalStorage)

```json
{
  "name": "User Name",
  "email": "user@example.com",
  "organization": "Organization",
  "role": "administrator",
  "level": "user",
  "registeredAt": "2024-01-01T00:00:00.000Z",
  "userId": "PROMIS-123456789"
}
```

### Format de Progression (LocalStorage)

```json
{
  "module1": {
    "lesson1": {
      "completed": true,
      "timestamp": "2024-01-01T00:00:00.000Z",
      "attempts": 1
    }
  }
}
```

## API et Intégrations

### LocalStorage Keys

- `promis_user` - Données utilisateur
- `promis_training_{role}_{level}` - Progression par rôle/niveau
- `promis_quiz_{quizId}` - Résultats des quiz

### Événements JavaScript

```javascript
// Initialisation
document.addEventListener('DOMContentLoaded', () => {
  Navigation.init();
  Interactive.initTooltips();
  ProgressTracker.updateProgressIndicators();
});

// Soumission de quiz
QuizManager.submitQuiz();

// Génération de certificat
CertificateGenerator.download(userData);
```

## Support et Contribution

### Obtenir de l'Aide
- Email: support@samaetat.sn
- Documentation: https://samaetat.sn/promis/docs
- Forum: https://forum.samaetat.sn

### Contribuer
- Signaler des bugs
- Suggérer des améliorations
- Soumettre des corrections
- Créer du contenu de formation

## Accessibilité

Le site de formation respecte les normes WCAG 2.1 AA:
- Contraste de couleurs suffisant
- Navigation au clavier
- Lecteurs d'écran compatibles
- Textes alternatifs pour les images
- Support de la réduction de mouvement

## Performance

### Optimisations Implémentées
- Lazy loading des images
- Minification CSS/JS (en production)
- Compression GZIP
- Cache navigateur
- CDN pour les bibliothèques

### Métriques Cibles
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Lighthouse Score: > 90

## Sécurité

### Mesures de Sécurité
- Pas de données sensibles stockées
- LocalStorage uniquement (pas de cookies)
- HTTPS obligatoire en production
- Validation côté client
- Protection XSS via sanitization

## Licence

LGPL-3 - Compatible avec Odoo Community Edition

## Auteurs

SAMA Transparent State Solutions
- Mamadou Mbagnick DOGUE
- Rassol DOGUE

## Remerciements

Merci à tous les contributeurs et utilisateurs du système SAMA PROMIS.

---

**Dernière mise à jour**: 2024
**Version**: 1.0.0

## Roadmap

### Version 1.1 (Q1 2025)
- [ ] Tutoriels vidéo intégrés
- [ ] Système de badges gamifiés
- [ ] Forum de discussion
- [ ] Chat en direct avec support

### Version 1.2 (Q2 2025)
- [ ] Application mobile (PWA)
- [ ] Mode hors ligne complet
- [ ] Synchronisation multi-appareils
- [ ] Intégration avec SAMA PROMIS (SSO)

### Version 2.0 (Q3 2025)
- [ ] Backend API pour gestion centralisée
- [ ] Tableau de bord administrateur
- [ ] Rapports et analytics avancés
- [ ] Certification en ligne supervisée

## Notes de Développement

### Conventions de Code
- Indentation: 2 espaces
- Nommage: camelCase pour JS, kebab-case pour CSS
- Commentaires: JSDoc pour les fonctions
- Commits: Convention Conventional Commits

### Tests
- Tests manuels pour chaque module
- Validation HTML/CSS (W3C)
- Tests de compatibilité navigateurs
- Tests d'accessibilité (axe DevTools)

### Déploiement
- Branche `main` pour production
- Branche `develop` pour développement
- Pull requests obligatoires
- Review avant merge

## FAQ Technique

**Q: Pourquoi utiliser LocalStorage au lieu d'une base de données?**
A: Pour un site statique sans backend, LocalStorage permet de sauvegarder la progression localement. Pour une version entreprise, une API backend serait recommandée.

**Q: Comment gérer plusieurs utilisateurs sur le même ordinateur?**
A: Actuellement, chaque navigateur/profil a ses propres données. Pour multi-utilisateurs, implémenter un système de connexion avec backend.

**Q: Les certificats sont-ils vérifiables?**
A: Les certificats contiennent un QR code et un ID unique. La vérification nécessiterait un backend pour valider l'authenticité.

**Q: Peut-on traduire le site en d'autres langues?**
A: Oui, la structure permet l'internationalisation. Créer des fichiers de traduction et implémenter un sélecteur de langue.

## Contact

Pour toute question ou suggestion concernant le site de formation:
- Email: formation@samaetat.sn
- Téléphone: +221 33 XXX XX XX
- Adresse: Dakar, Sénégal
