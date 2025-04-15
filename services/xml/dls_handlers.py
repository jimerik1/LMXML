# services/xml/dls_handlers.py
import logging
from datetime import datetime
from typing import Dict, List, Any
from lxml import etree as ET

from services.xml.utils import generate_random_id
from services.xml.element_operations import create_element, remove_existing_elements, find_group_element

logger = logging.getLogger(__name__)

def update_dls_overrides(root: ET.Element, well_id: str, wellbore_id: str, scenario_id: str, 
                        dls_group_id: str, dls_overrides: List[Dict[str, Any]]) -> bool:
    """
    Update dogleg severity overrides in the XML.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        scenario_id: Scenario ID
        dls_group_id: DLS override group ID
        dls_overrides: List of DLS override data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Updating DLS overrides for group {dls_group_id}")
        
        # Remove existing DLS override entries
        remove_existing_elements(root, f".//TU_DLS_OVERRIDE[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']")
        
        # Find the DLS override group element
        group_result = find_group_element(
            root,
            f".//TU_DLS_OVERRIDE_GROUP[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']",
            dls_group_id
        )
        
        if not group_result:
            return False
        
        _, parent_elem, group_index = group_result
        
        # Sort DLS overrides by top depth in descending order (deepest first)
        sorted_overrides = sorted(dls_overrides, key=lambda x: float(x.get('topDepth', 0)), reverse=True)
        
        # Add new DLS override elements
        for i, override in enumerate(sorted_overrides):
            # Generate a new ID for each override
            override_id = generate_random_id()

            # Create element attributes
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            element_attrs = {
                'WELL_ID': well_id,
                'WELLBORE_ID': wellbore_id,
                'SCENARIO_ID': scenario_id,
                'DLS_OVERRIDE_GROUP_ID': dls_group_id,
                'DLS_OVERRIDE_ID': override_id,
                'MD_TOP': str(override.get('topDepth')),
                'MD_BASE': str(override.get('baseDepth')),
                'DOGLEG_SEVERITY': str(override.get('doglegSeverity')),
                'CREATE_DATE': f"{{ts '{now}'}}",
                'CREATE_USER_ID': 'API_USER',
                'CREATE_APP_ID': 'XML_API',
                'UPDATE_DATE': f"{{ts '{now}'}}",
                'UPDATE_USER_ID': 'API_USER',
                'UPDATE_APP_ID': 'XML_API'
            }
            
            # Create the element
            element = create_element('TU_DLS_OVERRIDE', element_attrs)
            
            # Insert the element
            parent_elem.insert(group_index + 1 + i, element)
            
            logger.info(f"Added DLS override: {override.get('topDepth')}-{override.get('baseDepth')}, "
                       f"DLS={override.get('doglegSeverity')}")
        
        return True
    except Exception as e:
        logger.error(f"Error updating DLS overrides: {str(e)}", exc_info=True)
        return False