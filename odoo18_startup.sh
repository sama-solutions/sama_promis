#!/bin/bash

# odoo18_startup.sh - Script to start Odoo 18 and create a new database with master password
# Location: /home/grand-as/psagsn/custom_addons/sama_etat/odoo18_startup.sh

# Set to 1 to enable dependency check and installation
CHECK_DEPENDENCIES=1

# Always use a virtual environment
USE_VENV=1
# Virtual environment path will be set later
VENV_PATH=""

# Function to check and link SAMA_ETAT module
install_sama_etat() {
    echo "Checking for SAMA_ETAT_V1.2 STABLE module..."

    # Set the custom_addons directory path
    CUSTOM_ADDONS_PATH="/home/grand-as/psagsn/custom_addons"
    TARGET_MODULE_PATH="$CUSTOM_ADDONS_PATH/sama_etat"

    # Create custom_addons directory if it doesn't exist
    mkdir -p "$CUSTOM_ADDONS_PATH"

    # Known module location (as specified by user)
    SOURCE_MODULE_PATH="$CUSTOM_ADDONS_PATH/SAMA_ETAT_V1.2 STABLE"

    # Check if the source module exists
    if [ -d "$SOURCE_MODULE_PATH" ]; then
        echo "Found SAMA_ETAT module at: $SOURCE_MODULE_PATH"

        # Create a properly named module directory for Odoo
        if [ ! -d "$TARGET_MODULE_PATH" ]; then
            echo "Creating properly named module directory for Odoo..."
            # Create target directory if it doesn't exist
            mkdir -p "$TARGET_MODULE_PATH"

            # Copy all files from source to target
            cp -r "$SOURCE_MODULE_PATH"/* "$TARGET_MODULE_PATH"/

            # Fix spaces in XML files (external IDs)
            echo "Fixing spaces in external IDs..."
            find "$TARGET_MODULE_PATH" -name "*.xml" -type f -exec perl -i -pe 's/(id=")([^"]*)/${1}${2=~s| |_|gr}/ge' {} \;
            find "$TARGET_MODULE_PATH" -name "*.csv" -type f -exec sed -i 's/ /_/g' {} \;
            # Also fix manifest file if it uses spaces in module name
            if [ -f "$TARGET_MODULE_PATH/__manifest__.py" ]; then
                sed -i "s/'name': .*/'name': 'SAMA ETAT',/" "$TARGET_MODULE_PATH/__manifest__.py"
            fi

            echo "Module copied to Odoo-compatible directory: $TARGET_MODULE_PATH"
            return 0
        else
            echo "Module already exists in Odoo-compatible directory: $TARGET_MODULE_PATH"
            return 0
        fi
    fi

    # Fallback to checking various possible locations if the specified path doesn't exist
    POSSIBLE_LOCATIONS=(
        "$CUSTOM_ADDONS_PATH/SAMA_ETAT_V1.2_STABLE"
        "$CUSTOM_ADDONS_PATH/sama_etat"
        "$CUSTOM_ADDONS_PATH/SAMA_ETAT"
        "$ODOO_PATH/addons/SAMA_ETAT_V1.2 STABLE"
        "$ODOO_PATH/addons/SAMA_ETAT_V1.2_STABLE"
        "$ODOO_PATH/addons/sama_etat"
    )

    MODULE_FOUND=0
    for LOCATION in "${POSSIBLE_LOCATIONS[@]}"; do
        if [ -d "$LOCATION" ]; then
            echo "Found SAMA_ETAT module at: $LOCATION"
            MODULE_FOUND=1

            # If module is not in custom_addons with the proper name, create a proper copy
            if [[ "$LOCATION" != "$CUSTOM_ADDONS_PATH/sama_etat" ]]; then
                TARGET_PATH="$CUSTOM_ADDONS_PATH/sama_etat"

                if [ ! -e "$TARGET_PATH" ]; then
                    echo "Creating Odoo-compatible module directory..."
                    mkdir -p "$TARGET_PATH"

                    # Copy all files from source to target
                    cp -r "$LOCATION"/* "$TARGET_PATH"/

                    # Fix spaces in XML files (external IDs)
                    echo "Fixing spaces in external IDs..."
                    find "$TARGET_PATH" -name "*.xml" -type f -exec perl -i -pe 's/(id=")([^"]*)/${1}${2=~s| |_|gr}/ge' {} \;
                    find "$TARGET_PATH" -name "*.csv" -type f -exec sed -i 's/ /_/g' {} \;
                    # Also fix manifest file if it uses spaces in module name
                    if [ -f "$TARGET_PATH/__manifest__.py" ]; then
                        sed -i "s/'name': .*/'name': 'SAMA ETAT',/" "$TARGET_PATH/__manifest__.py"
                    fi

                    echo "Module copied to Odoo-compatible directory: $TARGET_PATH"
                else
                    echo "Module already exists in Odoo-compatible directory."
                fi
            fi

            break
        fi
    done

    if [ "$MODULE_FOUND" -eq 0 ]; then
        echo "SAMA_ETAT module not found in standard locations."
        echo "Enter the full path to SAMA_ETAT_V1.2 STABLE module"
        echo "(Or press Enter to skip module installation):"
        read -p "> " MODULE_PATH

        if [ -n "$MODULE_PATH" ] && [ -d "$MODULE_PATH" ]; then
            echo "Found module at: $MODULE_PATH"
            # Always use sama_etat as the target directory name for Odoo compatibility
            TARGET_PATH="$CUSTOM_ADDONS_PATH/sama_etat"

            if [ ! -e "$TARGET_PATH" ]; then
                echo "Copying SAMA_ETAT module to Odoo-compatible directory..."
                mkdir -p "$TARGET_PATH"
                cp -r "$MODULE_PATH"/* "$TARGET_PATH"/

                # Fix spaces in XML files (external IDs)
                echo "Fixing spaces in external IDs..."
                find "$TARGET_PATH" -name "*.xml" -type f -exec perl -i -pe 's/(id=")([^"]*)/${1}${2=~s| |_|gr}/ge' {} \;
                find "$TARGET_PATH" -name "*.csv" -type f -exec sed -i 's/ /_/g' {} \;
                # Also fix manifest file if it uses spaces in module name
                if [ -f "$TARGET_PATH/__manifest__.py" ]; then
                    sed -i "s/'name': .*/'name': 'SAMA ETAT',/" "$TARGET_PATH/__manifest__.py"
                fi

                echo "Module copied to: $TARGET_PATH"
            else
                echo "Module already exists at: $TARGET_PATH"
            fi
        elif [ -n "$MODULE_PATH" ]; then
            echo "Error: Could not find module at $MODULE_PATH"
        else
            echo "Module installation skipped."
        fi
    fi
}

# Function to check and configure PostgreSQL
setup_postgresql() {
    echo "Checking PostgreSQL configuration..."

    # Check if PostgreSQL is installed
    if ! command -v psql &> /dev/null; then
        echo "PostgreSQL is not installed. Installing..."
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-client
        echo "PostgreSQL installed."
    fi

    # Check if PostgreSQL service is running
    if ! systemctl is-active --quiet postgresql; then
        echo "Starting PostgreSQL service..."
        sudo systemctl start postgresql
    fi

    # Check if odoo user exists in PostgreSQL
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='odoo'" | grep -q 1; then
        echo "Creating PostgreSQL user 'odoo'..."
        sudo -u postgres psql -c "CREATE USER odoo WITH CREATEDB PASSWORD 'odoo';"
        echo "PostgreSQL user 'odoo' created."
    else
        echo "PostgreSQL user 'odoo' already exists."
    fi

    # Update pg_hba.conf to use MD5 authentication for the odoo user
    PG_HBA_FILE=$(sudo -u postgres psql -t -P format=unaligned -c "SHOW hba_file;")

    if ! sudo grep -q "local   all             odoo                                    md5" "$PG_HBA_FILE"; then
        echo "Updating PostgreSQL authentication settings..."
        # Add the configuration at the beginning of the file
        sudo sed -i '1i# Odoo user configuration - added by odoo18_startup.sh' "$PG_HBA_FILE"
        sudo sed -i '2ilocal   all             odoo                                    md5' "$PG_HBA_FILE"
        sudo sed -i '3ihost    all             odoo            127.0.0.1/32            md5' "$PG_HBA_FILE"
        sudo sed -i '4ihost    all             odoo            ::1/128                 md5' "$PG_HBA_FILE"

        # Reload PostgreSQL configuration
        echo "Reloading PostgreSQL configuration..."
        sudo systemctl reload postgresql
    else
        echo "PostgreSQL authentication already configured for user 'odoo'."
    fi

    echo "PostgreSQL configuration completed."
}

# Function to find odoo-bin in common locations
find_odoo_path() {
    # Common locations for Odoo installations
    COMMON_PATHS=(
        "/usr/lib/python3/dist-packages/odoo"
        "/opt/odoo"
        "/opt/odoo/odoo"
        "/usr/local/lib/python3.*/dist-packages/odoo"
        "$HOME/odoo"
        "$HOME/Odoo"
        "/var/lib/odoo"
    )

    # First check if ODOO_PATH environment variable is set
    if [ ! -z "$ODOO_PATH" ] && [ -f "$ODOO_PATH/odoo-bin" ]; then
        echo "$ODOO_PATH"
        return 0
    fi

    # Then check common locations
    for path in "${COMMON_PATHS[@]}"; do
        # Handle glob patterns
        for expanded_path in $path; do
            if [ -f "$expanded_path/odoo-bin" ]; then
                echo "$expanded_path"
                return 0
            fi
        done
    done

    # If not found in common locations, try to find it anywhere in /usr, /opt, and $HOME
    # This may take some time
    echo "Searching for odoo-bin in common system locations (this may take a moment)..."
    FOUND_PATH=$(find /usr /opt $HOME -name "odoo-bin" -type f 2>/dev/null | head -n 1)

    if [ ! -z "$FOUND_PATH" ]; then
        # Return the directory containing odoo-bin
        echo $(dirname "$FOUND_PATH")
        return 0
    fi

    # Not found
    return 1
}

# Function to check and install Python dependencies
check_dependencies() {
    echo "Checking for required Python dependencies..."

    # Common Odoo dependencies
    DEPENDENCIES=(
        "reportlab"
        "lxml"
        "pillow"
        "psycopg2-binary"
        "pydot"
        "pyopenssl"
        "pypdf2"
        "werkzeug"
        "xlsxwriter"
        "zeep"
        "python-ldap"
        "num2words"
        "polib"
        "requests"
        "vobject"
        "babel"
        "passlib"
        "decorator"
        "jinja2"
        "psutil"
        "gevent"
    )

    # System packages (apt) that correspond to Python packages
    APT_PACKAGES=(
        "python3-reportlab"
        "python3-lxml"
        "python3-pil"
        "python3-psycopg2"
        "python3-pydot"
        "python3-openssl"
        "python3-pypdf2"
        "python3-werkzeug"
        "python3-xlsxwriter"
        "python3-zeep"
        "python3-ldap"
        "python3-num2words"
        "python3-polib"
        "python3-requests"
        "python3-vobject"
        "python3-babel"
        "python3-passlib"
        "python3-decorator"
        "python3-jinja2"
        "python3-psutil"
        "python3-gevent"
    )

    MISSING=()

    # Only check dependencies if we're not using a virtual environment
    # (otherwise we'll install them in the venv later)
    if [ -z "$VENV_PATH" ]; then
        for dep in "${DEPENDENCIES[@]}"; do
            if ! $PYTHON_CMD -c "import $dep" 2>/dev/null; then
                MISSING+=("$dep")
            fi
        done

        if [ ${#MISSING[@]} -eq 0 ]; then
            echo "All dependencies are installed."
            return 0
        fi

        echo "Missing dependencies: ${MISSING[*]}"
        echo "Your Python environment is externally managed, which prevents pip installation."
        echo "You have two options:"
        echo "1. Create a virtual environment (recommended)"
        echo "2. Install dependencies via apt"

        read -p "Create a virtual environment? (Y/n): " venv_choice
        if [[ ! "$venv_choice" =~ ^[Nn]$ ]]; then
            # Create a virtual environment
            VENV_PATH="$PSAGSN_PATH/odoo18-venv"
            echo "Creating new virtual environment at $VENV_PATH..."

            # Make sure python3-venv is installed
            if ! dpkg -l | grep -q python3-venv; then
                echo "Installing python3-venv package..."
                echo "This may require sudo password"
                sudo apt-get update && sudo apt-get install -y python3-venv python3-full
            fi

            python3 -m venv "$VENV_PATH"
            if [ $? -ne 0 ]; then
                echo "Failed to create virtual environment."
                exit 1
            fi

            echo "Virtual environment created successfully!"
            echo "Installing dependencies in virtual environment..."
            source "$VENV_PATH/bin/activate"
            PYTHON_CMD="$VENV_PATH/bin/python"

            # Will install dependencies in the activate function below
            return 0
        else
            # Install via apt
            echo "Installing dependencies via apt..."
            echo "This may require sudo password"
            sudo apt-get update
            for pkg in "${APT_PACKAGES[@]}"; do
                echo "Installing $pkg..."
                sudo apt-get install -y $pkg
            done
            echo "Dependency installation completed."
        fi
    fi
}

# Flag to force reinstall of dependencies
REINSTALL_DEPS=0

# Flag to configure PostgreSQL
SETUP_POSTGRES=1

# Flag to install SAMA_ETAT module
INSTALL_SAMA_ETAT=0

# Default values
ODOO_PATH="/home/grand-as/psagsn/odoo18"
if [ ! -f "$ODOO_PATH/odoo-bin" ] && [ -z "$1" ]; then
    # Only use auto-detection if the default path doesn't exist and no arguments provided
    AUTO_PATH=$(find_odoo_path)
    if [ ! -z "$AUTO_PATH" ]; then
        ODOO_PATH="$AUTO_PATH"
    else
        echo "Error: Could not automatically find Odoo installation."
        echo "Please provide the path to your Odoo installation when running the script:"
        echo "./odoo18_startup.sh --odoo-path /path/to/your/odoo/installation"
        exit 1
    fi
fi

# Virtual environment is disabled by default
PSAGSN_PATH="/home/grand-as/psagsn"
ADDONS_PATH="$ODOO_PATH/addons,/home/grand-as/psagsn/custom_addons"
PYTHON_CMD="python3"
CONFIG_FILE="$PSAGSN_PATH/odoo18.conf"
LOG_FILE="$PSAGSN_PATH/odoo18.log"
PORT=8070
MASTER_PASSWORD=""
DB_NAME=""
DEMO_DATA="False"
LANGUAGE="fr_FR"
COUNTRY="MA"
CREATE_DB="False"
START_ODOO="True"
FIRST_RUN="True"

# Create PSAGSN directory if it doesn't exist
mkdir -p "$PSAGSN_PATH"

# Help function
function display_help {
    echo "Odoo 18 Startup Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Display this help message"
    echo "  -d, --database NAME        Specify the database name to create"
    echo "  -p, --password PASSWORD    Specify the master password"
    echo "  --odoo-path PATH           Specify the path to Odoo installation"
    echo "  --create-db                Create a new database"
    echo "  --no-start                 Don't start Odoo after creating database"
    echo "  --demo                     Load demo data (default: False)"
    echo "  --port PORT                Specify the port (default: 8070)"
    echo "  --lang LANGUAGE            Specify the language (default: fr_FR)"
    echo "  --country COUNTRY          Specify the country (default: MA)"
    echo "  --not-first-run            Indicate this is not the first run"
    echo "  --venv PATH                Specify the path to the virtual environment"
    echo "  --create-venv              Create a new virtual environment for Odoo"
    echo "  --no-venv                  Don't use a virtual environment"
    echo "  --reinstall-deps           Reinstall all dependencies (useful if you have dependency issues)"
    echo "  --setup-postgres           Configure PostgreSQL for Odoo (default: enabled)"
    echo "  --no-postgres-setup        Skip PostgreSQL configuration"
    echo "  --install-sama-etat        Install SAMA_ETAT_V1.2 STABLE module"
    echo "  --sama-etat-path PATH      Specify the path to SAMA_ETAT module"
    echo ""
    echo "Examples:"
    echo "  # Start Odoo without creating database:"
    echo "  $0 -p master_password"
    echo ""
    echo "  # Create a database and start Odoo:"
    echo "  $0 -d new_database -p master_password --create-db"
    echo ""
    echo "  # Create a database but don't start Odoo:"
    echo "  $0 -d new_database -p master_password --create-db --no-start"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            display_help
            exit 0
            ;;
        -d|--database)
            DB_NAME="$2"
            shift 2
            ;;
        -p|--password)
            MASTER_PASSWORD="$2"
            shift 2
            ;;
        --create-db)
            CREATE_DB="True"
            shift
            ;;
        --no-start)
            START_ODOO="False"
            shift
            ;;
        --not-first-run)
            FIRST_RUN="False"
            shift
            ;;
        --odoo-path)
            ODOO_PATH="$2"
            # Update the addons path accordingly
            ADDONS_PATH="$ODOO_PATH/addons,/home/grand-as/psagsn/custom_addons"
            shift 2
            ;;
        --venv)
            VENV_PATH="$2"
            shift 2
            ;;
        --no-venv)
            USE_VENV=0
            VENV_PATH=""
            shift
            ;;
        --reinstall-deps)
            # Flag to force reinstall of dependencies
            REINSTALL_DEPS=1
            shift
            ;;
        --setup-postgres)
            SETUP_POSTGRES=1
            shift
            ;;
        --no-postgres-setup)
            SETUP_POSTGRES=0
            shift
            ;;
        --install-sama-etat)
            INSTALL_SAMA_ETAT=1
            shift
            ;;
        --sama-etat-path)
            INSTALL_SAMA_ETAT=1
            SAMA_ETAT_PATH="$2"
            shift 2
            ;;
        --create-venv)
            # Create a new virtual environment in the PSAGSN directory
            VENV_PATH="$PSAGSN_PATH/odoo18-venv"
            echo "Creating new virtual environment at $VENV_PATH..."

            # Make sure python3-venv is installed
            if ! dpkg -l | grep -q python3-venv; then
                echo "Installing python3-venv package..."
                echo "This may require sudo password"
                sudo apt-get update && sudo apt-get install -y python3-venv python3-full
            fi

            python3 -m venv "$VENV_PATH"
            if [ $? -ne 0 ]; then
                echo "Failed to create virtual environment."
                exit 1
            fi
            echo "Virtual environment created successfully!"
            shift
            ;;
        --demo)
            DEMO_DATA="True"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --lang)
            LANGUAGE="$2"
            shift 2
            ;;
        --country)
            COUNTRY="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            display_help
            exit 1
            ;;
    esac
done

# Generate a random master password if not provided
if [ -z "$MASTER_PASSWORD" ]; then
    MASTER_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)

    # Display password in multiple ways to ensure visibility
    clear
    printf "\n\n\n"
    printf "\033[1;31m======================================================\033[0m\n"
    printf "\033[1;31m  MASTER PASSWORD: $MASTER_PASSWORD  \033[0m\n"
    printf "\033[1;31m  SAVE THIS PASSWORD FOR DATABASE OPERATIONS!  \033[0m\n"
    printf "\033[1;31m======================================================\033[0m\n"
    printf "\n\n\n"

    # Save to a separate file for reference
    echo "ODOO MASTER PASSWORD: $MASTER_PASSWORD" > "$PSAGSN_PATH/odoo_master_password.txt"
    echo "Generated on: $(date)" >> "$PSAGSN_PATH/odoo_master_password.txt"
    chmod 600 "$PSAGSN_PATH/odoo_master_password.txt"
    echo "Password saved to: $PSAGSN_PATH/odoo_master_password.txt"

    # Write to terminal directly to ensure visibility
    tput bold
    echo "================================================================="
    echo "                   MASTER PASSWORD: $MASTER_PASSWORD             "
    echo "================================================================="
    tput sgr0

    # Force user to acknowledge
    read -p "Press ENTER to continue after noting down the password..."
fi

# Ask for database name if creating a database and not provided
if [ "$CREATE_DB" = "True" ] && [ -z "$DB_NAME" ]; then
    read -p "Enter database name to create: " DB_NAME
fi

# Update addons path to include custom_addons and check for SAMA_ETAT module
CUSTOM_ADDONS_PATH="/home/grand-as/psagsn/custom_addons"
mkdir -p "$CUSTOM_ADDONS_PATH"
# Add custom_addons to addons_path if not already included
if [[ ! "$ADDONS_PATH" == *"$CUSTOM_ADDONS_PATH"* ]]; then
    ADDONS_PATH="$ADDONS_PATH,$CUSTOM_ADDONS_PATH"
fi

# Check if SAMA_ETAT module directories exist in any addons paths
if [[ "$INSTALL_SAMA_ETAT" -eq 1 ]]; then
    install_sama_etat
fi

# Create or update config file
cat > "$CONFIG_FILE" << EOF
[options]
addons_path = $ADDONS_PATH
admin_passwd = $MASTER_PASSWORD
data_dir = $PSAGSN_PATH/data
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
http_port = $PORT
logfile = $LOG_FILE
; Recommended Odoo settings for production use
workers = 2
max_cron_threads = 1
limit_time_cpu = 600
limit_time_real = 1200
EOF

echo "Configuration file created at: $CONFIG_FILE"
printf "\033[1;33mMaster password saved in configuration: \033[1;31m$MASTER_PASSWORD\033[0m\n"

# Check if Odoo path exists
if [ ! -f "$ODOO_PATH/odoo-bin" ]; then
    # Check if it might be a source installation where the structure is different
    if [ -f "$ODOO_PATH/odoo/odoo-bin" ]; then
        ODOO_PATH="$ODOO_PATH/odoo"
        # Update addons path accordingly
        ADDONS_PATH="$ODOO_PATH/addons,/home/grand-as/psagsn/custom_addons"
        echo "Found Odoo binary at $ODOO_PATH/odoo-bin"
    else
        echo "Error: Odoo not found at $ODOO_PATH"
        echo "Please specify the correct path to your Odoo installation:"
        echo "./odoo18_startup.sh --odoo-path /path/to/your/odoo/installation"
        echo ""
        echo "To find your Odoo installation, you can use this command:"
        echo "find / -name \"odoo-bin\" 2>/dev/null"
        exit 1
    fi
fi

echo "Using Odoo installation at: $ODOO_PATH"
echo "Addons path: $ADDONS_PATH"

# Create a virtual environment if needed and none exists
if [ "$USE_VENV" -eq 1 ] && [ -z "$VENV_PATH" ]; then
    VENV_PATH="$PSAGSN_PATH/odoo18-venv"

    if [ ! -d "$VENV_PATH" ]; then
        echo "Creating new virtual environment at $VENV_PATH..."

        # Make sure python3-venv is installed
        if ! dpkg -l | grep -q python3-venv; then
            echo "Installing python3-venv package..."
            echo "This may require sudo password"
            sudo apt-get update && sudo apt-get install -y python3-venv python3-full
        fi

        python3 -m venv "$VENV_PATH"
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment."
            echo "Continuing with system Python."
            VENV_PATH=""
        else
            echo "Virtual environment created successfully!"
        fi
    fi
fi

# Activate virtual environment and determine Python command
if [ ! -z "$VENV_PATH" ] && [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment at $VENV_PATH..."
    source "$VENV_PATH/bin/activate" || {
        echo "Failed to activate virtual environment. Path exists but activation failed."
        echo "Continuing without virtual environment..."
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
        elif command -v python &> /dev/null; then
            PYTHON_CMD="python"
        fi
    }

    # If activation was successful, use the Python from virtual environment
    if [ $? -eq 0 ]; then
        if [ -f "$VENV_PATH/bin/python" ]; then
            PYTHON_CMD="$VENV_PATH/bin/python"
        elif [ -f "$VENV_PATH/bin/python3" ]; then
            PYTHON_CMD="$VENV_PATH/bin/python3"
        fi
        echo "Virtual environment activated successfully."
        echo "To manually source this environment in the future, run:"
        echo "source $VENV_PATH/bin/activate"
    fi
else
    if [ ! -z "$VENV_PATH" ]; then
        echo "Warning: Virtual environment not found at $VENV_PATH"
        echo "To create a new virtual environment, run this script with --create-venv"
    else
        echo "Running without virtual environment (system Python)."
    fi

    # Check which Python is available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python not found. Please install Python 3 or specify the correct path."
        exit 1
    fi
fi

echo "Using Python command: $PYTHON_CMD"

# Check dependencies if enabled
if [ "$CHECK_DEPENDENCIES" -eq 1 ] || [ "$REINSTALL_DEPS" -eq 1 ]; then
    # If we're using a virtual environment, install dependencies in it
    if [ ! -z "$VENV_PATH" ] && [ -d "$VENV_PATH" ]; then
        echo "Installing base Odoo dependencies in virtual environment..."
        $PYTHON_CMD -m pip install -U pip wheel setuptools

        # Check if requirements.txt exists in Odoo directory
        if [ -f "$ODOO_PATH/requirements.txt" ]; then
            echo "Found requirements.txt in Odoo directory. Installing dependencies from it..."
            $PYTHON_CMD -m pip install -r "$ODOO_PATH/requirements.txt"
            # Still install lxml with html_clean explicitly as it's a special case
            $PYTHON_CMD -m pip install --upgrade "lxml[html_clean]"
            echo "Dependencies from requirements.txt installed."
        else
            echo "Installing Odoo dependencies manually..."
            $PYTHON_CMD -m pip install reportlab "lxml[html_clean]" pillow psycopg2-binary pydot pyopenssl pypdf2 werkzeug xlsxwriter zeep num2words polib requests vobject python-ldap babel passlib decorator jinja2 psutil gevent
            echo "Base dependencies installed in virtual environment."
        fi
    else
        # Otherwise check system dependencies
        check_dependencies
    fi
fi

# Create the data directory
mkdir -p "$PSAGSN_PATH/data"

# Configure PostgreSQL if enabled
if [ "$SETUP_POSTGRES" -eq 1 ]; then
    setup_postgresql
fi

# Check if sama_etat module already exists and fix external IDs if needed
if [ -d "$CUSTOM_ADDONS_PATH/sama_etat" ]; then
    echo "Checking and fixing external IDs in existing sama_etat module..."
    find "$CUSTOM_ADDONS_PATH/sama_etat" -name "*.xml" -type f -exec perl -i -pe 's/(id=")([^"]*)/${1}${2=~s| |_|gr}/ge' {} \;
    find "$CUSTOM_ADDONS_PATH/sama_etat" -name "*.csv" -type f -exec sed -i 's/ /_/g' {} \;
    # Also fix manifest file if it uses spaces in module name
    if [ -f "$CUSTOM_ADDONS_PATH/sama_etat/__manifest__.py" ]; then
        sed -i "s/'name': .*/'name': 'SAMA ETAT',/" "$CUSTOM_ADDONS_PATH/sama_etat/__manifest__.py"
    fi
    echo "Fixed potential spaces in external IDs"
fi

# Note: SAMA_ETAT module installation is now handled during addons_path configuration

# Always display the master password again before starting Odoo
printf "\n\n"
printf "\033[1;37;41m====================================================\033[0m\n"
printf "\033[1;37;41m  FINAL REMINDER - MASTER PASSWORD: $MASTER_PASSWORD  \033[0m\n"
printf "\033[1;37;41m  YOU WILL NEED THIS FOR DATABASE MANAGEMENT!  \033[0m\n"
printf "\033[1;37;41m====================================================\033[0m\n"
printf "\n\n"
cat "$PSAGSN_PATH/odoo_master_password.txt"
printf "\n\n"

# Write to terminal with different method for max compatibility
tput setaf 1; tput setab 7; tput bold
echo "****************************************************************"
echo "*                                                              *"
echo "*  MASTER PASSWORD: $MASTER_PASSWORD  *"
echo "*                                                              *"
echo "****************************************************************"
tput sgr0
echo ""

# Kill any running Odoo instances
echo "Checking for running Odoo instances..."
pkill -f "odoo-bin" || echo "No Odoo instances found running."
echo "Any running Odoo instances have been terminated."

# Set Python path to include Odoo directory
export PYTHONPATH="$ODOO_PATH:$PYTHONPATH"

# Create new database if requested
if [ "$CREATE_DB" = "True" ]; then
    if [ -z "$DB_NAME" ]; then
        echo "Error: Database name is required for database creation."
        exit 1
    fi

    echo "Creating new Odoo database: $DB_NAME"
    echo "This may take a few minutes..."

    # Using the Odoo command line to create a new database
    $PYTHON_CMD "$ODOO_PATH/odoo-bin" -c "$CONFIG_FILE" \
        --addons-path="$ADDONS_PATH" \
        --http-port="$PORT" \
        --logfile="$LOG_FILE" \
        -d "$DB_NAME" \
        --stop-after-init \
        --without-demo="$DEMO_DATA" \
        --language="$LANGUAGE" \
        --country="$COUNTRY" \
        --init=base

    result=$?

    # Check if database creation was successful
    if [ $result -eq 0 ]; then
        echo "Database $DB_NAME created successfully!"
    else
        echo "Failed to create database. Check the log file for more details: $LOG_FILE"
        exit 1
    fi
fi

# Start Odoo if requested
if [ "$START_ODOO" = "True" ]; then
    echo "Starting Odoo server..."

    DB_PARAM=""
    if [ ! -z "$DB_NAME" ]; then
        DB_PARAM="-d $DB_NAME"
    fi

    echo "Odoo will be accessible at: http://localhost:$PORT"
    echo "Log file: $LOG_FILE"
    echo "Configuration file: $CONFIG_FILE"

    # Display master password in plain text
    echo ""
    echo "======================================================================"
    echo "  MASTER PASSWORD FOR DATABASE OPERATIONS: $MASTER_PASSWORD"
    echo "======================================================================"
    echo ""

    if [ "$FIRST_RUN" = "True" ]; then
        echo ""
        tput bold
        echo "============== FIRST-TIME SETUP INSTRUCTIONS ==============="
        tput sgr0
        echo "1. Open http://localhost:$PORT in your browser"
        echo "2. You'll see the database creation page"
        echo "3. Enter your database information"
        tput bold; tput setaf 1
        echo "4. Use '$MASTER_PASSWORD' as the master password"
        tput sgr0
        echo "5. After creating the database, you'll be able to log in with the admin credentials you set"
        echo "6. To install the SAMA_ETAT module:"
        echo "   - Go to Apps menu"
        echo "   - Remove the 'Apps' filter if present"
        echo "   - Search for 'sama_etat'"
        echo "   - Click Install button next to the module"
        tput bold
        echo "============================================================"
        tput sgr0
    fi

    echo "Press Ctrl+C to stop Odoo"

    # Start Odoo with the configuration
    $PYTHON_CMD "$ODOO_PATH/odoo-bin" -c "$CONFIG_FILE" $DB_PARAM
else
    echo "Odoo server not started as per your request."
    echo "To start Odoo manually, run:"
    echo "  $0 -p $MASTER_PASSWORD"
    if [ ! -z "$DB_NAME" ]; then
        echo "  # Or to start with the created database:"
        echo "  $0 -p $MASTER_PASSWORD -d $DB_NAME"
    fi
fi

# Deactivate virtual environment if it was activated
if [ ! -z "$VENV_PATH" ] && [ -d "$VENV_PATH" ]; then
    echo "Deactivating virtual environment..."
    deactivate 2>/dev/null || true
fi
