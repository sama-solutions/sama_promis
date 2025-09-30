#!/bin/bash
# Installation script for SAMA PROMIS module dependencies

set -euo pipefail

ODOO_ENV=${ODOO_ENV:-odoo}
ODOO_CONFIG=${ODOO_CONFIG:-/etc/odoo/odoo.conf}
ODOO_DB=${ODOO_DB:-odoo}

printf "Installing python dependencies...\n"
if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt
else
    echo "No requirements.txt found, skipping Python dependency installation."
fi

printf "Ensuring qrcode dependency is available...\n"
python3 -m pip install qrcode

printf "Applying database migrations...\n"
${ODOO_ENV} -c "${ODOO_CONFIG}" -d "${ODOO_DB}" -u sama_promis

printf "Installation completed successfully.\n"
