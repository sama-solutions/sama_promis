# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Module Principal
==============================

Module principal pour SAMA PROMIS.
"""

# IMPORTANT: Charger shared en PREMIER pour que les mixins soient disponibles
from . import shared

# Ensuite charger les autres modules
from . import models
from . import controllers
from . import micromodules
