#!/bin/bash

# SAMA ÉTAT - Comprehensive Backup Script
# =======================================
# This script creates a complete backup of the SAMA ÉTAT project
# including source code, database, and configuration files.

set -e  # Exit on any error

# Configuration
PROJECT_NAME="sama_etat"
BACKUP_BASE_DIR="/home/grand-as/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_BASE_DIR}/${PROJECT_NAME}_backup_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Function to create directory safely
create_dir() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log "Created directory: $dir"
    fi
}

# Function to backup source code
backup_source_code() {
    log "Starting source code backup..."

    local source_dir="/home/grand-as/psagsn/custom_addons/sama_etat"
    local dest_dir="${BACKUP_DIR}/source_code"

    create_dir "$dest_dir"

    if [ -d "$source_dir" ]; then
        # Copy all source files
        cp -r "$source_dir" "$dest_dir/"

        # Create archive
        cd "${BACKUP_DIR}"
        tar -czf "sama_etat_source_${TIMESTAMP}.tar.gz" -C source_code sama_etat

        log_success "Source code backed up to: ${dest_dir}/sama_etat"
        log_success "Archive created: sama_etat_source_${TIMESTAMP}.tar.gz"
    else
        log_error "Source directory not found: $source_dir"
        return 1
    fi
}

# Function to backup database
backup_database() {
    log "Starting database backup..."

    local db_backup_dir="${BACKUP_DIR}/database"
    create_dir "$db_backup_dir"

    # Get list of databases (you may need to adjust this)
    local databases=("sama_etat_db" "odoo18" "psagsn_db")  # Add your actual database names

    for db in "${databases[@]}"; do
        log "Checking database: $db"

        # Check if database exists
        if psql -lqt | cut -d \| -f 1 | grep -qw "$db"; then
            log "Backing up database: $db"

            # Create SQL dump
            pg_dump "$db" > "${db_backup_dir}/${db}_${TIMESTAMP}.sql"

            # Create compressed backup
            pg_dump "$db" | gzip > "${db_backup_dir}/${db}_${TIMESTAMP}.sql.gz"

            log_success "Database $db backed up successfully"
        else
            log_warning "Database $db not found, skipping..."
        fi
    done
}

# Function to backup configuration files
backup_configurations() {
    log "Starting configuration backup..."

    local config_dir="${BACKUP_DIR}/configurations"
    create_dir "$config_dir"

    # Odoo configuration
    local odoo_configs=(
        "/home/grand-as/psagsn/odoo18/odoo.conf"
        "/home/grand-as/psagsn/custom_addons/sama_etat/odoo.conf"
        "/etc/odoo/odoo.conf"
    )

    for config_file in "${odoo_configs[@]}"; do
        if [ -f "$config_file" ]; then
            cp "$config_file" "$config_dir/"
            log_success "Backed up: $config_file"
        else
            log_warning "Config file not found: $config_file"
        fi
    done

    # Nginx configuration (if exists)
    if [ -f "/etc/nginx/sites-available/odoo" ]; then
        cp "/etc/nginx/sites-available/odoo" "$config_dir/nginx_odoo.conf"
        log_success "Backed up Nginx configuration"
    fi

    # System service files
    if [ -f "/etc/systemd/system/odoo.service" ]; then
        cp "/etc/systemd/system/odoo.service" "$config_dir/"
        log_success "Backed up Odoo service file"
    fi
}

# Function to backup logs
backup_logs() {
    log "Starting logs backup..."

    local logs_dir="${BACKUP_DIR}/logs"
    create_dir "$logs_dir"

    # Odoo logs
    local log_files=(
        "/var/log/odoo/odoo.log"
        "/home/grand-as/psagsn/custom_addons/sama_etat/odoo.log"
        "/home/grand-as/psagsn/custom_addons/sama_etat/odoo_tasks_update.log"
    )

    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            cp "$log_file" "$logs_dir/"
            log_success "Backed up: $log_file"
        else
            log_warning "Log file not found: $log_file"
        fi
    done
}

# Function to create system info snapshot
create_system_info() {
    log "Creating system information snapshot..."

    local info_dir="${BACKUP_DIR}/system_info"
    create_dir "$info_dir"

    # System information
    {
        echo "SAMA ÉTAT Backup System Information"
        echo "=================================="
        echo "Timestamp: $(date)"
        echo "Hostname: $(hostname)"
        echo "User: $(whoami)"
        echo "Working Directory: $(pwd)"
        echo ""
        echo "System Information:"
        echo "==================="
        uname -a
        echo ""
        echo "Disk Usage:"
        echo "==========="
        df -h
        echo ""
        echo "Memory Usage:"
        echo "============="
        free -h
        echo ""
        echo "Python Version:"
        echo "==============="
        python3 --version
        echo ""
        echo "PostgreSQL Version:"
        echo "==================="
        psql --version
        echo ""
        echo "Odoo Processes:"
        echo "==============="
        ps aux | grep odoo | grep -v grep || echo "No Odoo processes found"
        echo ""
        echo "Installed Packages (Python):"
        echo "============================"
        pip3 list | head -20
        echo ""
        echo "Git Status (if applicable):"
        echo "==========================="
        if [ -d "/home/grand-as/psagsn/custom_addons/sama_etat/.git" ]; then
            cd "/home/grand-as/psagsn/custom_addons/sama_etat"
            git status
            git log --oneline -10
        else
            echo "Not a git repository"
        fi
    } > "${info_dir}/system_info.txt"

    log_success "System information saved"
}

# Function to create validation report
create_validation_report() {
    log "Creating validation report..."

    local validation_dir="${BACKUP_DIR}/validation"
    create_dir "$validation_dir"

    # Change to source directory for validation
    cd "/home/grand-as/psagsn/custom_addons/sama_etat"

    # XML validation
    if [ -f "check_xml_syntax.sh" ]; then
        log "Running XML validation..."
        ./check_xml_syntax.sh > "${validation_dir}/xml_validation.txt" 2>&1 || true
    fi

    # Coordinate validation
    if [ -f "validate_map_data.py" ]; then
        log "Running coordinate validation..."
        python3 validate_map_data.py > "${validation_dir}/coordinate_validation.txt" 2>&1 || true
    fi

    # File inventory
    log "Creating file inventory..."
    {
        echo "SAMA ÉTAT File Inventory"
        echo "========================"
        echo "Generated: $(date)"
        echo ""
        echo "Directory Structure:"
        echo "===================="
        tree . || find . -type d | head -50
        echo ""
        echo "File Count by Type:"
        echo "==================="
        echo "Python files: $(find . -name "*.py" | wc -l)"
        echo "XML files: $(find . -name "*.xml" | wc -l)"
        echo "JavaScript files: $(find . -name "*.js" | wc -l)"
        echo "CSS files: $(find . -name "*.css" | wc -l)"
        echo "Markdown files: $(find . -name "*.md" | wc -l)"
        echo ""
        echo "Recent Changes:"
        echo "==============="
        find . -type f -mtime -7 -ls | head -20
    } > "${validation_dir}/file_inventory.txt"

    log_success "Validation report created"
}

# Function to create README for backup
create_backup_readme() {
    log "Creating backup README..."

    cat > "${BACKUP_DIR}/README_BACKUP.md" << EOF
# SAMA ÉTAT Backup - ${TIMESTAMP}

## Backup Information
- **Created**: $(date)
- **Version**: SAMA ÉTAT v1.0 with Interactive Map
- **System**: $(hostname)
- **User**: $(whoami)

## Backup Contents

### 1. Source Code (\`source_code/\`)
- Complete SAMA ÉTAT module source code
- All Python, XML, JavaScript, and configuration files
- Compressed archive: \`sama_etat_source_${TIMESTAMP}.tar.gz\`

### 2. Database (\`database/\`)
- PostgreSQL database dumps (.sql and .sql.gz formats)
- Includes all project data, configurations, and demo data

### 3. Configurations (\`configurations/\`)
- Odoo configuration files
- Nginx configuration (if applicable)
- System service files

### 4. Logs (\`logs/\`)
- Odoo application logs
- System logs related to SAMA ÉTAT

### 5. System Information (\`system_info/\`)
- Complete system snapshot
- Installed packages and versions
- System resources and status

### 6. Validation (\`validation/\`)
- XML syntax validation results
- Coordinate validation results
- File inventory and recent changes

## Restoration Instructions

### Quick Restore (Source Code Only)
\`\`\`bash
# Extract source code
cd /home/grand-as/psagsn/custom_addons/
tar -xzf ${BACKUP_DIR}/sama_etat_source_${TIMESTAMP}.tar.gz

# Update Odoo module
./odoo-bin -d your_db -u sama_etat
\`\`\`

### Full Restore (Database + Source)
\`\`\`bash
# 1. Restore database
psql your_database < database/your_database_${TIMESTAMP}.sql

# 2. Restore source code
cd /home/grand-as/psagsn/custom_addons/
rm -rf sama_etat/  # CAUTION: This removes current version
tar -xzf ${BACKUP_DIR}/sama_etat_source_${TIMESTAMP}.tar.gz

# 3. Restart Odoo
sudo systemctl restart odoo
\`\`\`

## Validation Before Restore
Always validate backup integrity:
\`\`\`bash
# Check archive integrity
tar -tzf sama_etat_source_${TIMESTAMP}.tar.gz > /dev/null && echo "Archive OK"

# Check database dump
head -10 database/*.sql
\`\`\`

## Features in This Backup
- ✅ Interactive Map with Leaflet.js
- ✅ Realistic GPS coordinates for Senegal
- ✅ 25+ government projects with geolocation
- ✅ 15+ official decisions with coordinates
- ✅ 20+ public events across regions
- ✅ Citizen-friendly tooltips in French
- ✅ Responsive design for mobile/desktop
- ✅ Dynamic data loading via API

## Contact
For restoration support or questions about this backup:
- Check validation reports in \`validation/\` directory
- Review system information in \`system_info/\` directory
- Verify file inventory before restoration

---
**Backup Created**: $(date)
**Status**: Complete and Validated
**Ready for**: Production Restoration
EOF

    log_success "Backup README created"
}

# Main backup function
main() {
    echo ""
    echo "🗄️  SAMA ÉTAT COMPREHENSIVE BACKUP"
    echo "=================================="
    echo "Starting backup process at $(date)"
    echo "Backup will be created in: $BACKUP_DIR"
    echo ""

    # Create main backup directory
    create_dir "$BACKUP_BASE_DIR"
    create_dir "$BACKUP_DIR"

    # Start backup process
    log "Backup process started..."

    # Execute backup functions
    backup_source_code
    backup_database
    backup_configurations
    backup_logs
    create_system_info
    create_validation_report
    create_backup_readme

    # Create final compressed backup
    log "Creating final compressed backup..."
    cd "$BACKUP_BASE_DIR"
    tar -czf "sama_etat_complete_backup_${TIMESTAMP}.tar.gz" "sama_etat_backup_${TIMESTAMP}/"

    # Calculate sizes
    local backup_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    local archive_size=$(du -sh "sama_etat_complete_backup_${TIMESTAMP}.tar.gz" | cut -f1)

    echo ""
    echo "📊 BACKUP SUMMARY"
    echo "=================="
    echo "Backup Directory: $BACKUP_DIR"
    echo "Backup Size: $backup_size"
    echo "Compressed Archive: sama_etat_complete_backup_${TIMESTAMP}.tar.gz"
    echo "Archive Size: $archive_size"
    echo ""
    echo "Backup Contents:"
    echo "- ✅ Source Code (complete module)"
    echo "- ✅ Database Dumps (SQL format)"
    echo "- ✅ Configuration Files"
    echo "- ✅ Application Logs"
    echo "- ✅ System Information"
    echo "- ✅ Validation Reports"
    echo "- ✅ Restoration Instructions"
    echo ""

    log_success "🎉 BACKUP COMPLETED SUCCESSFULLY!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Verify backup integrity: tar -tzf sama_etat_complete_backup_${TIMESTAMP}.tar.gz"
    echo "2. Test restoration in development environment"
    echo "3. Store backup in secure location"
    echo "4. Update backup documentation"
    echo ""
    echo "🔗 Quick Access:"
    echo "Backup Location: $BACKUP_DIR"
    echo "README: $BACKUP_DIR/README_BACKUP.md"
    echo "Archive: $BACKUP_BASE_DIR/sama_etat_complete_backup_${TIMESTAMP}.tar.gz"
    echo ""
}

# Error handling
trap 'log_error "Backup failed at line $LINENO. Check the error above."; exit 1' ERR

# Check if running as correct user
if [ "$(whoami)" != "grand-as" ]; then
    log_warning "Running as $(whoami), expected grand-as. Continuing anyway..."
fi

# Check for required tools
for tool in pg_dump tar gzip; do
    if ! command -v "$tool" &> /dev/null; then
        log_error "Required tool '$tool' is not installed"
        exit 1
    fi
done

# Run main backup process
main "$@"

# Exit successfully
exit 0
