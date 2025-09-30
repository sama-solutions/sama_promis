# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Micromodules Architecture
=======================================

Architecture modulaire pour SAMA PROMIS avec micromodules indépendants.
Chaque micromodule gère une fonctionnalité spécifique du système.
"""

# Import des micromodules
from . import core
from . import projects
# Public portal micromodule disabled - to be developed later
# from . import public_portal