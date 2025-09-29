# SAMA PROMIS Testing Guide

## Overview
This guide explains how to run automated tests and manual QA scenarios for the SAMA PROMIS module.

## Automated Tests

### Odoo Test Runner
- **Command**
  ```bash
  odoo-bin -c /etc/odoo/odoo.conf -d <database> -u sama_promis --test-enable --test-tags post_install
  ```
- **Scope**
  - Controller routes (`tests/test_controllers.py`)
  - Micromodule wiring (`tests/test_micromodules.py`)
  - Payment workflows (`tests/test_payment.py`)
  - Project workflow transitions (`tests/test_workflows.py`)
  - Public portal rendering (`tests/test_public_portal.py`)
  - QR code generation (`tests/test_qr_codes.py`)
  - Installation smoke tests (`tests/test_installation.py`)
  - Core models regression (`tests/test_models.py`)
  - Phase 2 feature coverage (`tests/test_phase2_features.py`)

### Helper Script
- **Command**
  ```bash
  ./scripts/run_tests.sh
  ```
- **Environment Variables**
  - `ODOO_ENV`: Binary or wrapper to execute Odoo (default `odoo`).
  - `ODOO_CONFIG`: Path to the configuration file (default `/etc/odoo/odoo.conf`).
  - `ODOO_DB`: Database name (default `odoo`).
  - `TEST_TAGS`: Custom test tags (default `post_install`).

## Manual QA Checklist

- **Contract creation**: Verify contracts can be created for each demo project.
- **Payment requests**: Submit, approve, and mark payments as paid.
- **Public portal**: Access `/promispublic`, navigate to project and donor detail pages.
- **QR code display**: Open a project form and ensure QR code fields populate without errors.
- **Workflow transitions**: Move a project through draft → submitted → approved → in progress → completed.
- **Micromodule sync**: Ensure micromodule actions appear in menus and dashboards refresh.
- **Controller security**: Confirm unauthorized users cannot POST to sensitive endpoints.

## Automation Scripts

- **Complete install & test**: `scripts/install_and_test.py`
  ```bash
  ./scripts/install_and_test.py -d <database> --config /etc/odoo/odoo.conf
  ```
  - Upgrades the module if `--upgrade` flag is provided.
  - Runs tests with `--test-enable` and configurable tags.

- **QR code validation**: `scripts/validate_qr_codes.py`
  ```bash
  ./scripts/validate_qr_codes.py -d <database> --url http://localhost:8069 --username admin --password admin
  ```
  - Verifies QR code data consistency over XML-RPC.
  - Use `--require-image` to fail when QR images are missing.

- **Workflow stress tests**: `scripts/test_workflows.py`
  ```bash
  ./scripts/test_workflows.py -d <database> --config /etc/odoo/odoo.conf --tags post_install
  ```
  - Runs only the workflow tagged tests with optional `--failfast`.
