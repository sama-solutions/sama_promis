
import os
from lxml import etree
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_odoo_views(module_path):
    """
    Fix Odoo view files by:
    - Removing deprecated type='tree' fields
    - Ensuring proper XML formatting
    - Validating view structures
    """
    views_dir = os.path.join(module_path, 'views')
    
    if not os.path.exists(views_dir):
        logger.error(f"Views directory not found at {views_dir}")
        return
    
    for filename in os.listdir(views_dir):
        if not filename.endswith('.xml'):
            continue
            
        filepath = os.path.join(views_dir, filename)
        logger.info(f"Processing {filepath}")
        
        try:
            # Parse XML file
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(filepath, parser)
            
            modified = False
            
            # Fix tree view types
            for record in tree.xpath("//record[@model='ir.ui.view']"):
                # Remove deprecated type field for tree views
                for field in record.xpath(".//field[@name='type']"):
                    if field.text == 'tree':
                        field.getparent().remove(field)
                        modified = True
                        logger.info(f"Removed deprecated type='tree' from view in {filename}")
            
            if modified:
                # Save changes with proper formatting
                tree.write(
                    filepath,
                    pretty_print=True,
                    encoding='utf-8',
                    xml_declaration=True
                )
                logger.info(f"Updated {filename}")
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    module_path = "/home/grand-as/psagsn/custom_addons/sama_etat"
    fix_odoo_views(module_path)
