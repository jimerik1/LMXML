# services/xml/binary_data.py
import os
import logging
from typing import Dict, List, Any, Optional
from lxml import etree as ET

from services.xml.utils import generate_random_id

logger = logging.getLogger(__name__)

def inject_binary_data(root: ET.Element, template_path: str) -> bool:
    """
    Inject binary data from binary_data_library.xml into the XML.
    
    Args:
        root: Root XML element
        template_path: Path to the template file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the template directory path
        template_dir = os.path.dirname(template_path)
        
        # Set the binary data library path
        binary_data_path = os.path.join(template_dir, 'binary_data_library.xml')
        
        logger.info(f"Looking for binary data at {binary_data_path}")
        
        if not os.path.exists(binary_data_path):
            logger.warning(f"Binary data library not found at {binary_data_path}")
            return False
        
        # Load binary data library
        binary_tree = ET.parse(binary_data_path)
        binary_root = binary_tree.getroot()
        
        # Find the BINARY_DATA element
        binary_data_elem = binary_root if binary_root.tag == 'BINARY_DATA' else binary_root.find(".//BINARY_DATA")
        
        if binary_data_elem is None:
            logger.warning("No BINARY_DATA element found in binary data library")
            return False
        
        logger.info("Found BINARY_DATA element in binary data library")
        
        # Check if there's already a BINARY_DATA element in our XML
        existing_binary = root.find(".//BINARY_DATA")
        if existing_binary is not None:
            logger.info("Removing existing BINARY_DATA element")
            parent = existing_binary.getparent()
            if parent is not None:
                parent.remove(existing_binary)
        
        # Create a new BINARY_DATA element in the export element
        binary_elem = ET.Element("BINARY_DATA")
        
        # Copy attributes
        for key, value in binary_data_elem.attrib.items():
            binary_elem.set(key, str(value))
        
        # Extract existing IDs from our XML
        entity_ids = extract_binary_data_entity_ids(root)
        
        # Process each attachment journal
        for journal_elem in binary_data_elem.findall("./CD_ATTACHMENT_JOURNAL"):
            logger.info("Processing CD_ATTACHMENT_JOURNAL element")
            
            # Create and add journal element
            new_journal = create_journal_element(journal_elem, entity_ids)
            binary_elem.append(new_journal)
        
        # Add the binary element to the root
        root.append(binary_elem)
        logger.info("Binary data injected successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error injecting binary data: {str(e)}", exc_info=True)
        return False

def extract_binary_data_entity_ids(root: ET.Element) -> Dict[str, List[str]]:
    """
    Extract entity IDs needed for binary data injection.
    
    Args:
        root: Root XML element
        
    Returns:
        Dictionary of entity ID lists
    """
    entity_ids = {
        'well_ids': [],
        'wellbore_ids': [],
        'scenario_ids': [],
        'site_ids': [],
        'project_ids': ['dzwLFOVy7l'],  # Hard-coded from template
        'policy_ids': ['Pzrgw9f4JC']    # Hard-coded from template
    }
    
    # Extract existing IDs
    for well_elem in root.xpath(".//CD_WELL"):
        entity_ids['well_ids'].append(well_elem.get('WELL_ID'))
    
    for wellbore_elem in root.xpath(".//CD_WELLBORE"):
        entity_ids['wellbore_ids'].append(wellbore_elem.get('WELLBORE_ID'))
    
    for scenario_elem in root.xpath(".//CD_SCENARIO"):
        entity_ids['scenario_ids'].append(scenario_elem.get('SCENARIO_ID'))
    
    for site_elem in root.xpath(".//CD_SITE"):
        entity_ids['site_ids'].append(site_elem.get('SITE_ID'))
    
    logger.debug(f"Found IDs in XML: well_ids={entity_ids['well_ids']}, "
                f"wellbore_ids={entity_ids['wellbore_ids']}, "
                f"scenario_ids={entity_ids['scenario_ids']}, "
                f"site_ids={entity_ids['site_ids']}")
    
    return entity_ids

def create_journal_element(journal_elem: ET.Element, entity_ids: Dict[str, List[str]]) -> ET.Element:
    """
    Create a new attachment journal element with updated IDs.
    
    Args:
        journal_elem: Original journal element
        entity_ids: Dictionary of entity ID lists
        
    Returns:
        Element: New journal element
    """
    # Create a new journal element
    new_journal = ET.Element("CD_ATTACHMENT_JOURNAL")
    
    # Generate new IDs for the attachments
    attachment_id = generate_random_id(8)
    attachment_journal_id = generate_random_id(8)
    
    # Copy and update attributes
    for key, value in journal_elem.attrib.items():
        if key == "ATTACHMENT_ID":
            new_journal.set(key, attachment_id)
        elif key == "ATTACHMENT_JOURNAL_ID":
            new_journal.set(key, attachment_journal_id)
        elif key == "ATTACHMENT_LOCATOR":
            # Create a new locator with our IDs
            new_locator = update_attachment_locator(value, entity_ids)
            new_journal.set(key, new_locator)
        else:
            new_journal.set(key, value)
    
    # Process the child CD_ATTACHMENT element
    for attachment_elem in journal_elem.findall("./CD_ATTACHMENT"):
        new_attachment = create_attachment_element(attachment_elem, attachment_id)
        new_journal.append(new_attachment)
    
    # Copy text content and trailing text if present
    if journal_elem.text and journal_elem.text.strip():
        new_journal.text = journal_elem.text
    
    # Copy the text after the attachment element (often binary data)
    if len(journal_elem) > 0 and journal_elem[-1].tail and journal_elem[-1].tail.strip():
        for i, child in enumerate(new_journal):
            if i == len(new_journal) - 1:  # Last child
                child.tail = journal_elem[-1].tail
    
    return new_journal

def update_attachment_locator(locator: str, entity_ids: Dict[str, List[str]]) -> str:
    """
    Update attachment locator string with new entity IDs.
    
    Args:
        locator: Original locator string
        entity_ids: Dictionary of entity ID lists
        
    Returns:
        str: Updated locator string
    """
    # Parse the locator string
    parts = {}
    for part in locator.split('+'):
        if '=' in part:
            name, id_value = part.split('=', 1)
            # Strip parentheses
            if id_value.startswith('(') and id_value.endswith(')'):
                id_value = id_value[1:-1]
            parts[name] = id_value
    
    # Update with our IDs
    id_mappings = {
        'POLICY_ID': 'policy_ids',
        'PROJECT_ID': 'project_ids',
        'SITE_ID': 'site_ids',
        'WELL_ID': 'well_ids',
        'WELLBORE_ID': 'wellbore_ids',
        'SCENARIO_ID': 'scenario_ids'
    }
    
    for name, list_name in id_mappings.items():
        if name in parts and entity_ids.get(list_name):
            parts[name] = entity_ids[list_name][0]
    
    # Reconstruct the locator string
    return '+'.join([f"{name}=({value})" for name, value in parts.items()])

def create_attachment_element(attachment_elem: ET.Element, attachment_id: str) -> ET.Element:
    """
    Create a new attachment element with updated ID.
    
    Args:
        attachment_elem: Original attachment element
        attachment_id: New attachment ID
        
    Returns:
        Element: New attachment element
    """
    new_attachment = ET.Element("CD_ATTACHMENT")
    
    # Copy and update attributes
    for key, value in attachment_elem.attrib.items():
        if key == "ATTACHMENT_ID":
            new_attachment.set(key, attachment_id)
        else:
            new_attachment.set(key, value)
    
    # Copy the binary data content
    if attachment_elem.text:
        new_attachment.text = attachment_elem.text
    
    # Copy any children of the attachment (if any)
    for child in attachment_elem:
        new_child = ET.fromstring(ET.tostring(child))
        new_attachment.append(new_child)
    
    return new_attachment