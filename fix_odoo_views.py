import os
import re
from xml.etree import ElementTree as ET

def fix_xml_views(directory):
    """
    Scan and fix Odoo XML view files to remove deprecated 'type' field for tree views
    """
    for dirpath, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                filepath = os.path.join(dirpath, file)
                try:
                    # Read file content
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file contains view definitions
                    if 'ir.ui.view' in content:
                        tree = ET.parse(filepath)
                        xml_root = tree.getroot()
                        modified = False

                        # Find view records
                        for record in xml_root.findall(".//record[@model='ir.ui.view']"):
                            type_field = record.find("./field[@name='type']")
                            if type_field is not None and type_field.text == 'tree':
                                record.remove(type_field)
                                modified = True
                        
                        if modified:
                            print(f"Fixing view in: {filepath}")
                            tree.write(filepath, encoding='utf-8', xml_declaration=True)
                            
                except ET.ParseError:
                    print(f"Warning: Could not parse {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {str(e)}")

if __name__ == "__main__":
    # Change this to your Odoo custom addons directory
    addons_path = "/home/grand-as/psagsn/custom_addons"
    fix_xml_views(addons_path)