#!/bin/bash

# SAMA ÉTAT XML Syntax Validation Script
# =====================================
# This script validates all XML files in the SAMA ÉTAT project
# to ensure they are syntactically correct before deployment.

echo "🔍 SAMA ÉTAT XML Syntax Validation"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counter variables
total_files=0
valid_files=0
invalid_files=0

# Function to validate XML file
validate_xml() {
    local file=$1
    echo -n "Checking $file... "

    if [ ! -f "$file" ]; then
        echo -e "${RED}FILE NOT FOUND${NC}"
        return 1
    fi

    if xmllint --noout "$file" 2>/dev/null; then
        echo -e "${GREEN}✅ VALID${NC}"
        return 0
    else
        echo -e "${RED}❌ INVALID${NC}"
        echo -e "${YELLOW}Error details:${NC}"
        xmllint --noout "$file" 2>&1 | sed 's/^/  /'
        return 1
    fi
}

echo ""
echo "🗂️  Validating data files..."
echo "----------------------------"

# Data files
data_files=(
    "data/demo_data.xml"
    "data/senegalese_locations_demo.xml"
    "data/government_projects_demo_data.xml"
    "data/government_decisions_demo.xml"
    "data/government_events_demo_data.xml"
    "data/ministries_demo_data.xml"
    "data/budgets_demo_data.xml"
    "data/strategic_objectives_demo_data.xml"
    "data/employees_demo_data.xml"
)

for file in "${data_files[@]}"; do
    total_files=$((total_files + 1))
    if validate_xml "$file"; then
        valid_files=$((valid_files + 1))
    else
        invalid_files=$((invalid_files + 1))
    fi
done

echo ""
echo "🎨 Validating view files..."
echo "---------------------------"

# View files
view_files=(
    "views/public_map.xml"
    "views/dashboard_views.xml"
    "views/website_homepage.xml"
    "views/website_about.xml"
    "views/government_project_views.xml"
    "views/government_decision_views.xml"
    "views/government_event_views.xml"
)

for file in "${view_files[@]}"; do
    total_files=$((total_files + 1))
    if validate_xml "$file"; then
        valid_files=$((valid_files + 1))
    else
        invalid_files=$((invalid_files + 1))
    fi
done

echo ""
echo "⚙️  Validating configuration files..."
echo "------------------------------------"

# Configuration files
config_files=(
    "__manifest__.py"
)

# Check manifest file (Python syntax)
echo -n "Checking __manifest__.py... "
if python3 -m py_compile "__manifest__.py" 2>/dev/null; then
    echo -e "${GREEN}✅ VALID${NC}"
    total_files=$((total_files + 1))
    valid_files=$((valid_files + 1))
else
    echo -e "${RED}❌ INVALID${NC}"
    echo -e "${YELLOW}Python syntax error in manifest${NC}"
    total_files=$((total_files + 1))
    invalid_files=$((invalid_files + 1))
fi

# Summary
echo ""
echo "📊 VALIDATION SUMMARY"
echo "===================="
echo "Total files checked: $total_files"
echo -e "Valid files: ${GREEN}$valid_files${NC}"
echo -e "Invalid files: ${RED}$invalid_files${NC}"

if [ $invalid_files -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL FILES ARE VALID!${NC}"
    echo "✅ Ready for Odoo module update"
    echo ""
    echo "Next steps:"
    echo "1. Update Odoo module: ./odoo-bin -d your_db -u sama_etat"
    echo "2. Test public dashboard: http://your-server/senegal2050/dashboard"
    echo "3. Verify map functionality"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  VALIDATION FAILED${NC}"
    echo "Please fix the invalid files before proceeding."
    echo ""
    echo "Common fixes:"
    echo "- Check XML tag matching (opening/closing)"
    echo "- Verify proper nesting structure"
    echo "- Ensure special characters are escaped"
    exit 1
fi
