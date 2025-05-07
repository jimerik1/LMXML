# utils/xml_helpers.py
from lxml import etree as ET
import re
import logging
from typing import Dict, Any, Optional, Union, List, Tuple

logger = logging.getLogger(__name__)

# Define standard attribute order
ATTRIBUTE_ORDER = [
    # Primary entities
    "WELL_ID", "WELLBORE_ID", "SITE_ID", "PROJECT_ID",
    # Secondary entities  
    "ASSEMBLY_ID", "ASSEMBLY_COMP_ID", "SCENARIO_ID", "CASE_ID",
    "DATUM_ID", "ORIGINAL_TUBULAR_DATUM_ID",
    "DLS_OVERRIDE_GROUP_ID", "DLS_OVERRIDE_ID",
    "TEMP_GRADIENT_GROUP_ID", "TEMP_GRADIENT_ID",
    "PORE_PRESSURE_GROUP_ID", "PORE_PRESSURE_ID", 
    "FRAC_GRADIENT_GROUP_ID", "FRAC_GRADIENT_ID",
    "DEF_SURVEY_HEADER_ID", "DEFINITIVE_SURVEY_ID",
    # Entity identifiers
    "PACKER_NAME", "NAME", "PHASE", "TIGHT_GROUP_ID", "WELLBORE_NAME", "WELL_COMMON_NAME", 
    # Structural attributes
    "IS_LINKED", "SEQUENCE_NO", "IS_ACTIVE", "IS_READONLY", "IS_OFFSHORE",
    # Physical attributes
    "STRING_TYPE", "STRING_CLASS", "ASSEMBLY_SIZE", "HOLE_SIZE", "ASSEMBLY_NAME", "CASE_NAME",
    "MD_ASSEMBLY_TOP", "MD_ASSEMBLY_BASE", "MD_TOC",
    "TOP_DEPTH", "BASE_DEPTH", "MD_TOP", "MD_BASE", "LENGTH", "DEPTH",
    # Creation/update metadata (always at the end)
    "CREATE_DATE", "CREATE_USER_ID", "CREATE_APP_ID", 
    "UPDATE_DATE", "UPDATE_USER_ID", "UPDATE_APP_ID"
]

def set_attributes_ordered(element: ET.Element, attributes: Dict[str, Any]) -> None:
    """
    Set attributes on an XML element in a consistent order.
    
    Args:
        element: The XML element
        attributes: Dictionary of attribute name-value pairs
    """
    # First set attributes in the defined order
    for attr in ATTRIBUTE_ORDER:
        if attr in attributes:
            element.set(attr, str(attributes[attr]))
    
    # Then set any remaining attributes that weren't in our order list
    for attr, value in attributes.items():
        if attr not in ATTRIBUTE_ORDER:
            element.set(attr, str(value))

def load_xml_template(template_path: str) -> ET.ElementTree:
    """
    Load an XML template from a file path.
    
    Args:
        template_path: Path to the XML template
        
    Returns:
        ElementTree: Parsed XML template
        
    Raises:
        Exception: If template loading fails
    """
    try:
        return ET.parse(template_path)
    except Exception as e:
        logger.error(f"Failed to load XML template: {str(e)}")
        raise Exception(f"Failed to load XML template: {str(e)}")

def convert_camel_to_xml_key(camel_case_key: str) -> str:
    """
    Convert camelCase to UPPER_SNAKE_CASE for XML keys.
    
    Args:
        camel_case_key: camelCase key
        
    Returns:
        str: UPPER_SNAKE_CASE key
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_key)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

def find_element_by_attributes(root: ET.Element, tag_name: str, 
                              attributes: Dict[str, str]) -> Optional[ET.Element]:
    """
    Find an XML element by tag name and attribute values.
    
    Args:
        root: Root XML element
        tag_name: Tag name to search for
        attributes: Attribute key-value pairs to match
        
    Returns:
        Element: Found element or None
    """
    elements = root.findall(f".//{tag_name}")
    for element in elements:
        matches = True
        for attr, value in attributes.items():
            if element.get(attr) != str(value):
                matches = False
                break
        if matches:
            return element
    return None

def create_or_update_element(parent: ET.Element, tag_name: str, 
                            attributes: Dict[str, Any]) -> ET.Element:
    """
    Create or update an XML element with specified attributes.
    
    Args:
        parent: Parent XML element
        tag_name: Tag name for the element
        attributes: Attribute key-value pairs
        
    Returns:
        Element: Created or updated element
    """
    element = ET.SubElement(parent, tag_name)
    set_attributes_ordered(element, attributes)
    return element

def get_xml_string(self) -> str:
    """
    Get the XML as a string with proper formatting.
    
    Returns:
        str: Formatted XML string
    """
    from utils.xml_helpers import format_xml_with_line_breaks
    
    # Get the XML string
    xml_string = ET.tostring(self.root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    
    # Replace the XML declaration with the standard format including DataServices PI
    xml_string = xml_string.replace('<?xml version=\'1.0\' encoding=\'utf-8\'?>', 
                  '<?xml version="1.0" standalone="no"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>')
    
    # Apply explicit formatting with line breaks
    xml_string = format_xml_with_line_breaks(xml_string)
    
    return xml_string

def format_xml_with_line_breaks(xml_string: str) -> str:
    """
    Force line breaks after each XML tag, regardless of pretty_print setting.
    
    Args:
        xml_string: Input XML string
        
    Returns:
        str: XML string with line breaks after each tag
    """
    # Add line break after each closing tag
    xml_string = xml_string.replace('><', '>\n<')
    
    # Add line breaks after self-closing tags
    xml_string = xml_string.replace('/>', '/>\n')
    
    # Ensure proper line break after xml declaration
    xml_string = xml_string.replace('?>', '?>\n')
    
    return xml_string

def format_timestamp(date_str: str) -> Optional[str]:
    """
    Format a date string as a timestamp for the XML.
    
    Args:
        date_str: Date string in format 'YYYY-MM-DD HH:MM:SS'
        
    Returns:
        str: Formatted timestamp string like "{ts '2025-04-02 16:36:52'}"
    """
    if not date_str:
        return None
    
    return f"{{ts '{date_str}'}}"