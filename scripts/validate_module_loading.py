#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Module Loading Validation Script
==============================================

Validates that all models, mixins, and dependencies are correctly loaded.
"""

import sys
import os

# Colors for terminal output
CLASS_GREEN = '\033[92m'
CLASS_RED = '\033[91m'
CLASS_YELLOW = '\033[93m'
CLASS_RESET = '\033[0m'

def print_success(message):
    print(f"{CLASS_GREEN}✓ {message}{CLASS_RESET}")

def print_error(message):
    print(f"{CLASS_RED}✗ {message}{CLASS_RESET}")

def print_warning(message):
    print(f"{CLASS_YELLOW}⚠ {message}{CLASS_RESET}")

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print_success(f"{description} exists: {filepath}")
        return True
    else:
        print_error(f"{description} missing: {filepath}")
        return False

def check_import_order(filepath):
    """Check the import order in __init__.py files."""
    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if 'shared' is imported before 'models'
    shared_pos = content.find('from . import shared')
    models_pos = content.find('from . import models')
    
    if shared_pos == -1:
        print_error(f"'shared' module not imported in {filepath}")
        return False
    
    if models_pos == -1:
        print_warning(f"'models' module not imported in {filepath}")
        return True
    
    if shared_pos < models_pos:
        print_success(f"Import order correct in {filepath}: shared before models")
        return True
    else:
        print_error(f"Import order incorrect in {filepath}: shared must be before models")
        return False

def check_model_name(filepath, expected_name):
    """Check if a model has the correct _name."""
    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if f"_name = '{expected_name}'" in content:
        print_success(f"Model name correct in {filepath}: {expected_name}")
        return True
    else:
        print_error(f"Model name incorrect or missing in {filepath}: expected {expected_name}")
        return False

def check_mixin_inheritance(filepath, mixin_name):
    """Check if a model correctly inherits from a mixin."""
    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if f"'{mixin_name}'" in content and '_inherit' in content:
        print_success(f"Mixin inheritance found in {filepath}: {mixin_name}")
        return True
    else:
        print_warning(f"Mixin inheritance not found in {filepath}: {mixin_name}")
        return False

def main():
    """Main validation function."""
    print("\n" + "="*60)
    print("SAMA PROMIS - Module Loading Validation")
    print("="*60 + "\n")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.dirname(base_path)  # Go up one level from scripts/
    
    all_checks_passed = True
    
    # Check 1: Verify mixin files exist
    print("\n[1] Checking Mixin Files...")
    all_checks_passed &= check_file_exists(
        os.path.join(module_path, 'shared/mixins/workflow_mixin.py'),
        "Workflow Mixin"
    )
    all_checks_passed &= check_file_exists(
        os.path.join(module_path, 'shared/mixins/audit_mixin.py'),
        "Audit Mixin"
    )
    
    # Check 2: Verify import order in main __init__.py
    print("\n[2] Checking Import Order...")
    all_checks_passed &= check_import_order(
        os.path.join(module_path, '__init__.py')
    )
    
    # Check 3: Verify model names
    print("\n[3] Checking Model Names...")
    all_checks_passed &= check_model_name(
        os.path.join(module_path, 'models/call_for_proposal.py'),
        'sama.promis.call.proposal'
    )
    all_checks_passed &= check_model_name(
        os.path.join(module_path, 'shared/mixins/workflow_mixin.py'),
        'sama.promis.workflow.mixin'
    )
    all_checks_passed &= check_model_name(
        os.path.join(module_path, 'shared/mixins/audit_mixin.py'),
        'sama.promis.audit.mixin'
    )
    
    # Check 4: Verify mixin inheritance
    print("\n[4] Checking Mixin Inheritance...")
    all_checks_passed &= check_mixin_inheritance(
        os.path.join(module_path, 'models/compliance_task.py'),
        'sama.promis.workflow.mixin'
    )
    all_checks_passed &= check_mixin_inheritance(
        os.path.join(module_path, 'micromodules/core/models/base_model.py'),
        'sama.promis.workflow.mixin'
    )
    all_checks_passed &= check_mixin_inheritance(
        os.path.join(module_path, 'micromodules/core/models/base_model.py'),
        'sama.promis.audit.mixin'
    )
    
    # Check 5: Verify call_for_proposal references
    print("\n[5] Checking call_for_proposal References...")
    micromodule_project_file = os.path.join(module_path, 'micromodules/projects/models/project.py')
    if os.path.exists(micromodule_project_file):
        with open(micromodule_project_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "'sama.promis.call.proposal'" in content:
            print_success("Correct model name in micromodules/projects/models/project.py")
        elif "'sama.promis.call.for.proposal'" in content:
            print_error("Incorrect model name in micromodules/projects/models/project.py: should be 'sama.promis.call.proposal'")
            all_checks_passed = False
        else:
            print_warning("No call_for_proposal reference found in micromodules/projects/models/project.py")
    
    # Check 6: Verify One2many relation
    print("\n[6] Checking One2many Relations...")
    call_file = os.path.join(module_path, 'models/call_for_proposal.py')
    if os.path.exists(call_file):
        with open(call_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "One2many('project.project', 'call_for_proposal_id'" in content:
            print_success("Correct One2many relation in call_for_proposal.py")
        elif "One2many('sama.promis.project', 'call_for_proposal_id'" in content:
            print_error("Incorrect One2many relation in call_for_proposal.py: should point to 'project.project'")
            all_checks_passed = False
        else:
            print_warning("No One2many relation found in call_for_proposal.py")
    
    # Final result
    print("\n" + "="*60)
    if all_checks_passed:
        print_success("ALL CHECKS PASSED! Module should load correctly.")
        print("="*60 + "\n")
        return 0
    else:
        print_error("SOME CHECKS FAILED! Please fix the issues above.")
        print("="*60 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
