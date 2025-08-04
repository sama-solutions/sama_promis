# SAMA ÉTAT - Installation Guide

This guide provides instructions to set up and run the SAMA ÉTAT Odoo module.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python 3.12+**: Odoo 18 requires Python 3.12 or later.
*   **PostgreSQL**: A PostgreSQL server (version 14 or higher is recommended for Odoo 18).
*   **Git**: For cloning the repository.
*   **Odoo 18**: This module is designed for Odoo 18. You should have a working Odoo 18 installation or be prepared to set one up. This guide assumes you have the `odoo-bin` executable and a basic `odoo.conf` file.

## Step-by-Step Installation

### 1. Clone the Repository

First, clone the `sama-etat` repository to your local machine. It's recommended to clone it into your Odoo 18 `addons` path or a custom addons path.

```bash
git clone https://github.com/loi200812/sama-etat.git /path/to/your/odoo18/addons/sama_etat
```
Replace `/path/to/your/odoo18/addons/sama_etat` with the actual path where you want to place the module.

### 2. Set up a Python Virtual Environment (Recommended)

It's highly recommended to use a Python virtual environment to manage dependencies.

```bash
cd /path/to/your/odoo18/addons/sama_etat # Navigate to the module directory or your Odoo root
python3 -m venv odoo18-venv
source odoo18-venv/bin/activate
```

### 3. Install Python Dependencies

Install the Python libraries required by Odoo and the `sama_etat` module.

```bash
pip install -r /path/to/your/odoo18/requirements.txt # Install Odoo's dependencies first
pip install qrcode pillow psycopg2-binary # Specific dependencies for sama_etat
```
**Note:** `psycopg2-binary` is for PostgreSQL connectivity. If you encounter issues, you might need `psycopg2` (which requires PostgreSQL development headers).

### 4. Configure Odoo

Ensure your `odoo.conf` file is correctly configured. Key parameters include:

*   `addons_path`: Make sure this includes the path to your `sama_etat` module.
    ```ini
    [options]
    addons_path = /path/to/your/odoo18/addons,/path/to/your/odoo18/addons/sama_etat
    ; Replace with your actual Odoo addons path and the path to sama_etat
    ```
*   `db_user`, `db_password`, `db_host`, `db_port`: Your PostgreSQL database connection details.

### 5. PostgreSQL Database Setup

Create a PostgreSQL user and a database for your Odoo instance.

```bash
sudo -u postgres psql
CREATE USER odoo_user WITH PASSWORD 'odoo_password';
ALTER ROLE odoo_user CREATEDB;
\q
```
Replace `odoo_user` and `odoo_password` with your desired credentials.

### 6. Start Odoo and Install/Update Modules

For the initial setup or after significant module changes, you should start Odoo with the `-u all` flag to update all modules and ensure all views and assets are correctly loaded.

```bash
# Navigate to your Odoo 18 root directory where odoo-bin is located
cd /path/to/your/odoo18/

# Example command to start Odoo with update
# Ensure your virtual environment is activated if you're using one
nohup /path/to/odoo18-venv/bin/python3 odoo-bin \
    -c /path/to/your/odoo.conf \
    -u all \
    --logfile=/path/to/your/odoo.log \
    --log-level=info \
    > /path/to/your/odoo_startup.log 2>&1 &
```
Replace `/path/to/your/odoo18-venv/bin/python3` with your virtual environment's Python executable, and `/path/to/your/odoo.conf` with your Odoo configuration file.

**Important:** The `-u all` flag will update all modules. This can take some time. After the initial update, you can remove `-u all` for faster restarts.

### 7. Access Odoo and Install `SAMA ÉTAT`

1.  Open your web browser and navigate to `http://localhost:8069` (or your configured Odoo address).
2.  If it's a new database, follow the prompts to create a new database.
3.  Log in as an administrator.
4.  **Activate Developer Mode:**
    *   Go to `Settings`.
    *   Scroll down to the bottom of the page and click on "Activate the developer mode" (or "Activate the developer mode (with assets)").
5.  **Install `SAMA ÉTAT` and its dependencies:**
    *   Go to the "Apps" menu.
    *   Remove the "Apps" filter to see all modules.
    *   Search for "SAMA ÉTAT".
    *   Click the "Install" button. Odoo will automatically install its dependencies, including `Website Event` (`website_event`). If `Website Event` is not installed, search for it and install it manually first.

### 8. Verify Installation

After installation, you should be able to access the public pages and features of the SAMA ÉTAT module, including:

*   Public Dashboard: `/senegal2050/dashboard`
*   Public Project Page: `/senegal2050/project/<project_id>`
*   Public Event Page: `/senegal2050/event/<event_id>`
*   Public Decision Page: `/senegal2050/decision/<decision_id>`
*   Public Ministry Page: `/senegal2050/ministry/<ministry_id>`
*   Public Objective Page: `/senegal2050/objective/<objective_id>`
*   Public Axis Page: `/senegal2050/axis/<axis_id>`
*   Public Pillar Page: `/senegal2050/pillar/<pillar_id>`

If you encounter any issues, check your Odoo server logs (`odoo.log`) for detailed error messages.
