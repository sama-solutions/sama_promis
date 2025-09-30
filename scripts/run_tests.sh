#!/bin/bash
# Helper script to run SAMA PROMIS test suite

set -euo pipefail

ODOO_ENV=${ODOO_ENV:-odoo}
ODOO_CONFIG=${ODOO_CONFIG:-/etc/odoo/odoo.conf}
ODOO_DB=${ODOO_DB:-odoo}
TEST_TAGS=${TEST_TAGS:-"post_install"}

printf "Running tests for tags: %s\n" "${TEST_TAGS}"
${ODOO_ENV} -c "${ODOO_CONFIG}" -d "${ODOO_DB}" --test-tags "${TEST_TAGS}" -u sama_promis

printf "Tests executed successfully.\n"
