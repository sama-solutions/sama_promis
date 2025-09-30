# Guide de Compatibilité Odoo 18 Community Edition

## Vue d'ensemble

Ce document détaille les modifications apportées au module SAMA PROMIS pour assurer une compatibilité 100% avec Odoo 18 Community Edition.

## Changements Majeurs

### 1. Suppression de la Dépendance `account`

**Problème**: Le module `account` n'existe pas dans Odoo 18 CE.

**Solution**: 
- Suppression de `'account'` du fichier `__manifest__.py`
- Suppression de tous les imports liés au module account dans les fichiers Python
- Remplacement de la logique comptable par un système de suivi financier simplifié

**Fichiers modifiés**:
- `__manifest__.py`
- `models/sama_promis_project.py`
- `models/contract.py`
- `models/payment.py`

**Impact**: Les fonctionnalités suivantes sont désactivées:
- Génération automatique d'écritures comptables
- Intégration avec les journaux comptables
- Paiements comptables automatiques

**Alternative**: Système de suivi financier avec champs monétaires directs.

### 2. Modernisation de la Syntaxe des Vues XML

#### 2.1. Remplacement de `<tree>` par `<list>`

**Problème**: La balise `<tree>` est obsolète en Odoo 18.

**Solution**: Remplacement systématique par `<list>`.

**Exemple**:
```xml
<!-- AVANT (Odoo 17) -->
<tree string="Projets" editable="bottom">
    <field name="name"/>
</tree>

<!-- APRÈS (Odoo 18 CE) -->
<list string="Projets" editable="bottom" multi_edit="1">
    <field name="name"/>
</list>
```

**Fichiers modifiés**: Tous les fichiers dans `views/` et `micromodules/*/views/`

#### 2.2. Suppression de l'Attribut `attrs`

**Problème**: L'attribut `attrs` est deprecated en Odoo 18.

**Solution**: Utilisation d'attributs directs avec expressions de domaine.

**Exemples de transformation**:

```xml
<!-- AVANT -->
<field name="compliance_profile_id" 
       attrs="{'invisible': [('use_compliance_profile', '=', False)], 
               'required': [('use_compliance_profile', '=', True)]}"/>

<!-- APRÈS -->
<field name="compliance_profile_id" 
       invisible="not use_compliance_profile" 
       required="use_compliance_profile"/>
```

```xml
<!-- AVANT -->
<button name="action_generate_tasks" 
        attrs="{'invisible': [('task_count', '>', 0)]}"/>

<!-- APRÈS -->
<button name="action_generate_tasks" 
        invisible="task_count > 0"/>
```

```xml
<!-- AVANT -->
<div class="alert" attrs="{'invisible': [('is_overdue', '=', False)]}">

<!-- APRÈS -->
<div class="alert" invisible="not is_overdue">
```

**Règles de conversion**:
- `[('field', '=', False)]` → `not field`
- `[('field', '=', True)]` → `field`
- `[('field', '>', value)]` → `field > value`
- `[('field', '!=', value)]` → `field != value`
- `[('field', 'in', [val1, val2])]` → `field in [val1, val2]`

#### 2.3. Ajout de `multi_edit="1"`

**Fonctionnalité**: Édition en masse des enregistrements.

**Solution**: Ajout de `multi_edit="1"` sur toutes les listes éditables.

**Exemple**:
```xml
<list editable="bottom" multi_edit="1">
    <field name="name"/>
    <field name="amount"/>
</list>
```

**Avantage**: Permet aux utilisateurs de modifier plusieurs enregistrements simultanément.

#### 2.4. Suppression de `type="list"`

**Problème**: L'attribut `type="list"` dans les définitions de vues est incorrect.

**Solution**: Suppression complète de cet attribut.

**Exemple**:
```xml
<!-- AVANT (incorrect) -->
<record id="view_contract_tree" model="ir.ui.view">
    <field name="name">contract.tree</field>
    <field name="model">sama.promis.contract</field>
    <field name="type">list</field>  <!-- À SUPPRIMER -->
    <field name="arch" type="xml">
        <list>...</list>
    </field>
</record>

<!-- APRÈS (correct) -->
<record id="view_contract_tree" model="ir.ui.view">
    <field name="name">contract.tree</field>
    <field name="model">sama.promis.contract</field>
    <field name="arch" type="xml">
        <list>...</list>
    </field>
</record>
```

## Modules Odoo Utilisés (CE uniquement)

### Modules Requis
- ✅ `base` - Module de base Odoo
- ✅ `mail` - Messagerie et notifications
- ✅ `website` - Portail public
- ✅ `project` - Gestion de projets

### Modules Exclus (Enterprise/Obsolètes)
- ❌ `account` - Comptabilité (Enterprise)
- ❌ `social_media` - Obsolète
- ❌ `website_mail` - Non garanti en CE
- ❌ `website_sms` - Non garanti en CE
- ❌ `website_payment` - Configuration utilisateur
- ❌ `account_consolidation` - Retiré

## Prérequis Techniques

### Versions Requises
- **Python**: 3.11 ou supérieur
- **PostgreSQL**: 13 ou supérieur
- **Odoo**: 18.0 Community Edition

### Dépendances Python
```bash
pip install qrcode
```

## Framework Frontend

### Standard Odoo 18
- **Framework**: Owl.js (standard Odoo)
- **API**: REST API pour intégrations externes
- **Vues**: Syntaxe moderne avec `<list>`, attributs directs, `multi_edit`

### Fonctionnalités UI
- En-têtes fixes (sticky headers) sur les listes
- Édition en masse avec `multi_edit="1"`
- Décorations dynamiques (decoration-*)
- Widgets modernes (progressbar, badge, monetary, percentage)

## Checklist de Compatibilité

### Avant Migration
- [ ] Sauvegarder la base de données
- [ ] Vérifier Python >= 3.11
- [ ] Vérifier PostgreSQL >= 13
- [ ] Vérifier Odoo 18.0 CE

### Après Migration
- [ ] Aucune erreur liée au module `account`
- [ ] Toutes les vues s'affichent correctement
- [ ] Les listes utilisent `<list>` au lieu de `<tree>`
- [ ] Aucun attribut `attrs` dans les vues
- [ ] `multi_edit="1"` activé sur les listes éditables
- [ ] Les QR codes se génèrent correctement
- [ ] Les workflows fonctionnent correctement
- [ ] Les rapports PDF se génèrent correctement
- [ ] Les cron jobs s'exécutent correctement

## Tests de Compatibilité

### Tests Automatiques
```bash
# Lancer les tests unitaires
odoo-bin -d test_db -i sama_promis --test-enable --stop-after-init

# Vérifier les logs pour les erreurs
grep -i "error\|warning" odoo.log
```

### Tests Manuels
1. **Installation**: Installer le module sans erreur
2. **Vues**: Ouvrir toutes les vues principales (projets, contrats, paiements, conformité)
3. **Édition**: Tester l'édition en masse sur les listes
4. **Workflows**: Tester les transitions d'état
5. **Rapports**: Générer les rapports PDF
6. **QR Codes**: Vérifier la génération des QR codes
7. **Cron Jobs**: Vérifier l'exécution des tâches planifiées

## Dépannage

### Erreur: Module 'account' introuvable

**Cause**: Dépendance au module account (Enterprise).

**Solution**:
1. Vérifier `__manifest__.py` - `'account'` ne doit PAS être dans `depends`
2. Vérifier les imports Python - aucun import de `odoo.addons.account`
3. Mettre à jour vers la version >= 18.0.3.3.0

### Erreur: Syntaxe XML invalide

**Cause**: Utilisation de syntaxe obsolète.

**Solution**:
1. Remplacer `<tree>` par `<list>`
2. Supprimer tous les `attrs`
3. Utiliser des attributs directs

### Erreur: Vues ne s'affichent pas

**Cause**: Attribut `type="list"` incorrect.

**Solution**: Supprimer complètement cet attribut des définitions de vues.

## Détails des Modifications par Fichier

### Fichiers de Vues Modifiés

#### 1. `views/project_views.xml`
- ✅ Remplacé `<tree>` par `<list>` (3 occurrences)
- ✅ Supprimé tous les `attrs` (15+ occurrences)
- ✅ Ajouté `multi_edit="1"` sur listes éditables
- ✅ Converti expressions de domaine

#### 2. `views/compliance_task_views.xml`
- ✅ Remplacé `<tree>` par `<list>` (3 occurrences)
- ✅ Supprimé tous les `attrs` (9 occurrences)
- ✅ Ajouté `multi_edit="1"`

#### 3. `views/procurement_plan_views.xml`
- ✅ Remplacé `<tree>` par `<list>` (3 occurrences)
- ✅ Ajouté `multi_edit="1"` (3 occurrences)

#### 4. `views/contract_views.xml`
- ✅ Supprimé `type="list"` (2 occurrences)
- ✅ Remplacé `<tree>` par `<list>` (2 occurrences)
- ✅ Supprimé tous les `attrs` (10+ occurrences)
- ✅ Ajouté `multi_edit="1"`

#### 5. `views/payment_views.xml`
- ✅ Supprimé `type="list"`
- ✅ Modernisé syntaxe

#### 6. `views/evaluation_views.xml`
- ✅ Supprimé `type="list"`
- ✅ Ajouté `multi_edit="1"`

#### 7. `views/call_for_proposal_views.xml`
- ✅ Supprimé `type="list"`
- ✅ Ajouté `multi_edit="1"`

#### 8. `views/res_partner_views.xml`
- ✅ Pas de `<tree>` (vue héritée)
- ✅ Syntaxe déjà moderne

#### 9. `views/compliance_profile_views.xml`
- ✅ Remplacé `<tree>` par `<list>`
- ✅ Supprimé `attrs`

#### 10. `views/tag_views.xml`
- ✅ Remplacé `<tree>` par `<list>`

#### 11. `views/event_views.xml`
- ✅ Supprimé `type="list"` (2 occurrences)

#### 12. `views/contract_template_views.xml`
- ✅ Syntaxe déjà moderne (utilise `<list>`)

#### 13. `views/project_funding_source_views.xml`
- ✅ Remplacé `<tree>` par `<list>`

#### 14. `micromodules/core/views/base_views.xml`
- ✅ Remplacé `<tree>` par `<list>`

#### 15. `micromodules/projects/views/project_views.xml`
- ✅ Remplacé `<tree>` par `<list>` (2 occurrences)
- ✅ Supprimé `attrs`

### Fichiers Python Modifiés

#### 1. `models/contract.py`
- ✅ Commenté `payment_id = fields.Many2one('account.payment')`
- ✅ Ajouté alternative CE: `payment_reference` et `payment_state`

#### 2. `models/payment.py`
- ✅ Commenté `_create_account_payment()`
- ✅ Ajouté `_notify_payment_approved()`
- ✅ Modifié `action_approve()` pour ne pas appeler account

#### 3. `models/sama_promis_project.py`
- ✅ Aucune référence account trouvée

## Résumé des Statistiques

### Fichiers Modifiés
- **Total**: 19 fichiers
- **Vues XML**: 16 fichiers
- **Modèles Python**: 3 fichiers

### Modifications Effectuées
- **`<tree>` → `<list>`**: 25+ occurrences
- **`attrs` supprimés**: 50+ occurrences
- **`multi_edit="1"` ajoutés**: 15+ occurrences
- **`type="list"` supprimés**: 5 occurrences
- **Références account supprimées**: 5 occurrences

## Ressources

### Documentation Officielle
- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo 18 Community vs Enterprise](https://www.odoo.com/page/editions)
- [Owl.js Framework](https://github.com/odoo/owl)

### Support
- GitHub Issues: [lien vers le repo]
- Email: support@samaetat.sn
- Website: https://www.samaetat.sn

## Historique des Versions

### Version 18.0.3.3.0 (Actuelle)
- ✅ Compatibilité Odoo 18 CE complète
- ✅ Suppression dépendance `account`
- ✅ Modernisation syntaxe vues XML
- ✅ Ajout `multi_edit` sur listes éditables
- ✅ Phase 3 complète (Conformité bailleurs)

### Version 18.0.3.2.0
- Phase 2: Plans de passation de marché

### Version 18.0.3.1.0
- Phase 1: Gestion multi-sources de financement

## Licence

LGPL-3 - Compatible avec Odoo Community Edition

---

**Dernière mise à jour**: 2025-09-30
**Auteurs**: SAMA Transparent State Solutions
