# services/xml/element_operations.py
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from lxml import etree as ET

from services.xml.utils import format_xpath

logger = logging.getLogger(__name__)

def update_element_attribute(root: ET.Element, tag_name: str, id_attr: str, 
                            id_value: str, attr_name: str, attr_value: Any) -> bool:
    """
    Update a specific attribute in an element identified by its tag and ID.
    
    Args:
        root: Root XML element
        tag_name: Element tag name (e.g., 'CD_SITE')
        id_attr: ID attribute name (e.g., 'SITE_ID')
        id_value: ID attribute value to match
        attr_name: Attribute name to update
        attr_value: New attribute value
        
    Returns:
        bool: True if element was found and updated, False otherwise
    """
    xpath = format_xpath(tag_name, id_attr, id_value)
    elements = root.xpath(xpath)
    
    if not elements:
        logger.warning(f"No elements found for xpath: {xpath}")
        return False
    
    for element in elements:
        element.set(attr_name, str(attr_value))
        logger.debug(f"Updated attribute {attr_name}={attr_value} for element {tag_name}")
        
        # Update the timestamp if it's not an update date
        if attr_name not in ['CREATE_DATE', 'UPDATE_DATE']:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            element.set('UPDATE_DATE', f"{{ts '{now}'}}")
            element.set('UPDATE_USER_ID', 'API_USER')
            element.set('UPDATE_APP_ID', 'XML_API')
    
    return True

def update_element_name(root: ET.Element, tag_name: str, id_attr: str, 
                       id_value: str, name_value: str) -> bool:
    """
    Update the name attribute of an element identified by its tag and ID.
    
    Args:
        root: Root XML element
        tag_name: Element tag name (e.g., 'CD_SITE')
        id_attr: ID attribute name (e.g., 'SITE_ID')
        id_value: ID attribute value to match
        name_value: New name value
        
    Returns:
        bool: True if element was found and updated, False otherwise
    """
    # Determine the name attribute based on the tag
    name_attr_map = {
        'CD_SITE': 'SITE_NAME',
        'CD_WELL': 'WELL_COMMON_NAME',
        'CD_WELLBORE': 'WELLBORE_NAME',
        'CD_DATUM': 'DATUM_NAME',
        'CD_ASSEMBLY': 'ASSEMBLY_NAME',
        'CD_CASE': 'CASE_NAME',
    }
    
    name_attr = name_attr_map.get(tag_name, 'NAME')
    
    result = update_element_attribute(root, tag_name, id_attr, id_value, name_attr, name_value)
    if result:
        logger.info(f"Updated {name_attr} to '{name_value}' for {tag_name} with {id_attr}={id_value}")
    return result

def create_element(tag_name: str, attributes: Dict[str, Any]) -> ET.Element:
    """
    Create a new XML element with the specified attributes.
    
    Args:
        tag_name: Element tag name
        attributes: Dictionary of attribute name-value pairs
        
    Returns:
        Element: The created element
    """
    element = ET.Element(tag_name)
    for attr, value in attributes.items():
        element.set(attr, str(value))
    logger.debug(f"Created new element {tag_name} with attributes: {attributes}")
    return element

def remove_existing_elements(root: ET.Element, xpath: str) -> None:
    """
    Remove existing elements matching the given XPath.
    
    Args:
        root: Root XML element
        xpath: XPath to find elements to remove
    """
    elements = root.xpath(xpath)
    logger.debug(f"Removing {len(elements)} elements matching: {xpath}")
    for element in elements:
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)

def find_group_element(root: ET.Element, xpath: str, 
                     group_id: str) -> Optional[Tuple[ET.Element, ET.Element, int]]:
    """
    Find a group element and its parent by XPath.
    
    Args:
        root: Root XML element
        xpath: XPath to find the group element
        group_id: ID of the group to find
        
    Returns:
        Tuple of (group_element, parent_element, index) or None if not found
    """
    group_elements = root.xpath(xpath)
    
    if not group_elements:
        logger.warning(f"Group element not found with XPath: {xpath}")
        return None
    
    group_elem = group_elements[0]
    parent_elem = group_elem.getparent()
    group_index = parent_elem.index(group_elem)
    
    return group_elem, parent_elem, group_index

def extract_entity_ids(root: ET.Element) -> Dict[str, str]:
    """
    Extract various entity IDs from the XML.
    
    Args:
        root: Root XML element
        
    Returns:
        Dictionary of entity IDs
    """
    entity_ids = {
        'well_id': None,
        'wellbore_id': None,
        'site_id': None,
        'scenario_id': None,
        'temp_gradient_group_id': None,
        'pore_pressure_group_id': None,
        'frac_gradient_group_id': None,
        'dls_override_group_id': None,
        'survey_header_id': None,
        'datum_id': None
    }
    
    # Find site element and extract ID
    site_elements = root.xpath(".//CD_SITE")
    if site_elements:
        entity_ids['site_id'] = site_elements[0].get('SITE_ID')
        logger.info(f"Found site ID: {entity_ids['site_id']}")
    
    # Find well element and extract ID
    well_elements = root.xpath(".//CD_WELL")
    if well_elements:
        entity_ids['well_id'] = well_elements[0].get('WELL_ID')
        logger.info(f"Found well ID: {entity_ids['well_id']}")
    
    # Find wellbore element and extract ID
    wellbore_elements = root.xpath(".//CD_WELLBORE")
    if wellbore_elements:
        entity_ids['wellbore_id'] = wellbore_elements[0].get('WELLBORE_ID')
        logger.info(f"Found wellbore ID: {entity_ids['wellbore_id']}")
    
    # Find scenario element and extract IDs
    scenario_elements = root.xpath(".//CD_SCENARIO")
    if scenario_elements:
        entity_ids['scenario_id'] = scenario_elements[0].get('SCENARIO_ID')
        entity_ids['temp_gradient_group_id'] = scenario_elements[0].get('TEMP_GRADIENT_GROUP_ID')
        entity_ids['pore_pressure_group_id'] = scenario_elements[0].get('PORE_PRESSURE_GROUP_ID')
        entity_ids['frac_gradient_group_id'] = scenario_elements[0].get('FRAC_GRADIENT_GROUP_ID')
        entity_ids['survey_header_id'] = scenario_elements[0].get('DEF_SURVEY_HEADER_ID')
        entity_ids['datum_id'] = scenario_elements[0].get('DATUM_ID')
        logger.debug(f"Found scenario IDs: {entity_ids['scenario_id']}, temp_group: {entity_ids['temp_gradient_group_id']}")
    
    # Find DLS override group and extract ID
    dls_group_elements = root.xpath(".//TU_DLS_OVERRIDE_GROUP")
    if dls_group_elements:
        entity_ids['dls_override_group_id'] = dls_group_elements[0].get('DLS_OVERRIDE_GROUP_ID')
        logger.info(f"Found DLS override group ID: {entity_ids['dls_override_group_id']}")
    
    return entity_ids

def update_project_info(root: ET.Element, project_info: Dict[str, Any], 
                       entity_ids: Dict[str, str]) -> None:
    """
    Update project information in the XML.
    
    Args:
        root: Root XML element
        project_info: Project information data
        entity_ids: Dictionary of entity IDs
    """
    # Update site information
    if 'site' in project_info and entity_ids['site_id']:
        site = project_info['site']
        if 'siteName' in site:
            update_element_name(root, 'CD_SITE', 'SITE_ID', 
                               entity_ids['site_id'], site['siteName'])
    
    # Update well information
    if 'well' in project_info and entity_ids['well_id']:
        well = project_info['well']
        if 'wellCommonName' in well:
            update_element_name(root, 'CD_WELL', 'WELL_ID', 
                               entity_ids['well_id'], well['wellCommonName'])
    
    # Update wellbore information
    if 'wellbore' in project_info and entity_ids['wellbore_id']:
        wellbore = project_info['wellbore']
        if 'wellboreName' in wellbore:
            update_element_name(root, 'CD_WELLBORE', 'WELLBORE_ID', 
                               entity_ids['wellbore_id'], wellbore['wellboreName'])
    
    # Update scenario name if provided
    if entity_ids['scenario_id'] and 'well' in project_info and 'wellCommonName' in project_info['well']:
        update_element_name(root, 'CD_SCENARIO', 'SCENARIO_ID', 
                           entity_ids['scenario_id'], project_info['well']['wellCommonName'])

def update_datum(root: ET.Element, datum: Dict[str, Any], entity_ids: Dict[str, str]) -> None:
    """
    Update datum information in the XML.
    
    Args:
        root: Root XML element
        datum: Datum information data
        entity_ids: Dictionary of entity IDs
    """
    if not datum or not entity_ids['datum_id']:
        return
    
    if 'datumName' in datum:
        update_element_name(root, 'CD_DATUM', 'DATUM_ID', 
                           entity_ids['datum_id'], datum['datumName'])
    
    if 'datumElevation' in datum:
        update_element_attribute(root, 'CD_DATUM', 'DATUM_ID', 
                                entity_ids['datum_id'], 'DATUM_ELEVATION', datum['datumElevation'])