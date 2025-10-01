# SAMA PROMIS - Ordre de Chargement des Modules

## Problèmes Résolus

Ce document explique les problèmes critiques d'ordre de chargement qui ont été résolus.

## Problème 1: Mixins Non Disponibles

### Symptôme
```
ValueError: Model not found: sama.promis.workflow.mixin
ValueError: Model not found: sama.promis.audit.mixin
```

### Cause
Le module `shared` (contenant les mixins) n'était pas importé dans le `__init__.py` principal.

### Solution
Dans `__init__.py`:
```python
# AVANT (incorrect):
from . import models
from . import controllers
from . import micromodules

# APRÈS (correct):
from . import shared        # DOIT être en premier!
from . import models
from . import controllers
from . import micromodules
```

### Modèles Affectés
- `sama.promis.compliance.task` (hérite de `sama.promis.workflow.mixin`)
- `sama.promis.base.model` (hérite de `sama.promis.workflow.mixin` et `sama.promis.audit.mixin`)
- `sama.promis.procurement.plan` (hérite de `sama.promis.workflow.mixin`)
- Tous les modèles qui héritent de `sama.promis.base.model`

---

## Problème 2: Nom de Modèle Incorrect

### Symptôme
```
ValueError: Invalid field 'call_for_proposal_id' on model 'sama.promis.project'
```

### Cause
Le modèle s'appelle `sama.promis.call.proposal` mais était référencé comme `sama.promis.call.for.proposal` dans le micromodule projects.

### Solution
Dans `micromodules/projects/models/project.py` ligne 200:
```python
# AVANT (incorrect):
call_for_proposal_id = fields.Many2one(
    'sama.promis.call.for.proposal',  # INCORRECT
    ...
)

# APRÈS (correct):
call_for_proposal_id = fields.Many2one(
    'sama.promis.call.proposal',  # CORRECT
    ...
)
```

### Nom Correct du Modèle
Le modèle est défini dans `models/call_for_proposal.py` ligne 8:
```python
_name = 'sama.promis.call.proposal'
```

Toutes les références doivent utiliser exactement ce nom.

---

## Problème 3: Relation One2many Incorrecte

### Symptôme
```
ValueError: Field 'call_for_proposal_id' does not exist in model 'sama.promis.project'
```

### Cause
La relation One2many dans `call_for_proposal.py` pointait vers `sama.promis.project` mais le champ inverse existe dans `project.project` (extension Odoo).

### Solution
Dans `models/call_for_proposal.py` ligne 46:
```python
# AVANT (incorrect):
project_ids = fields.One2many('sama.promis.project', 'call_for_proposal_id',
                            string="Projets Soumis")

# APRÈS (correct):
project_ids = fields.One2many('project.project', 'call_for_proposal_id',
                            string="Projets Soumis")
```

### Explication
Il existe DEUX modèles de projet dans SAMA PROMIS:

1. **`project.project`** (dans `models/project.py`):
   - Extension du modèle Odoo standard
   - Utilisé pour les projets opérationnels
   - Contient le champ `call_for_proposal_id` (ligne 21)

2. **`sama.promis.project`** (dans `models/sama_promis_project.py`):
   - Modèle personnalisé SAMA PROMIS
   - Utilisé pour les projets de développement
   - Contient aussi un champ `call_for_proposal_id` (ligne 329)

La relation One2many doit pointer vers `project.project` car c'est le modèle principal pour les projets liés aux appels à propositions.

---

## Ordre de Chargement Correct

### Chaîne d'Import

```
__init__.py (racine)
  ↓
  ├─ shared/
  │   ├─ utils/
  │   └─ mixins/
  │       ├─ workflow_mixin.py  → sama.promis.workflow.mixin
  │       └─ audit_mixin.py     → sama.promis.audit.mixin
  ↓
  ├─ models/
  │   ├─ compliance_task.py     → hérite de sama.promis.workflow.mixin ✓
  │   ├─ call_for_proposal.py
  │   └─ ...
  ↓
  ├─ micromodules/
  │   ├─ core/
  │   │   └─ models/
  │   │       └─ base_model.py  → hérite de sama.promis.workflow.mixin ✓
  │   └─ projects/
  │       └─ models/
  │           └─ project.py     → référence sama.promis.call.proposal ✓
  ↓
  └─ controllers/
```

### Règles d'Ordre de Chargement

1. **Mixins en premier**: `shared` doit être importé avant tout autre module
2. **Models ensuite**: Les modèles peuvent utiliser les mixins
3. **Micromodules après**: Les micromodules peuvent utiliser les mixins et les models
4. **Controllers en dernier**: Les contrôleurs utilisent les models

---

## Vérification Post-Correction

### Commandes de Test

```bash
# Mettre à jour le module
odoo-bin -d your_database -u sama_promis --stop-after-init

# Vérifier les logs pour les erreurs
grep -i "error\|warning" odoo.log | grep -i "sama.promis"

# Lancer les tests
odoo-bin -d test_db -i sama_promis --test-enable --stop-after-init
```

### Checklist de Vérification

- [ ] Aucune erreur "Model not found" pour les mixins
- [ ] Le modèle `sama.promis.compliance.task` se charge correctement
- [ ] Le modèle `sama.promis.base.model` se charge correctement
- [ ] La relation `call_for_proposal.project_ids` fonctionne
- [ ] La relation `project.project.call_for_proposal_id` fonctionne
- [ ] Tous les tests passent

---

## Références

- **Mixins**: `/shared/mixins/workflow_mixin.py`, `/shared/mixins/audit_mixin.py`
- **Models affectés**: `compliance_task.py`, `base_model.py`, `procurement_plan.py`
- **Relations affectées**: `call_for_proposal.py` ↔ `project.py`

---

**Date de résolution**: 2024
**Version**: 18.0.4.0.1
