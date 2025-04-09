# utils/xml_helpers.py
import xml.etree.ElementTree as ET
import re
from lxml import etree

def load_xml_template(template_path):
    """
    Load an XML template from a file path.
    
    Args:
        template_path (str): Path to the XML template
        
    Returns:
        ElementTree: Parsed XML template
        
    Raises:
        Exception: If template loading fails
    """
    try:
        return etree.parse(template_path)
    except Exception as e:
        raise Exception(f"Failed to load XML template: {str(e)}")

def convert_camel_to_xml_key(camel_case_key):
    """
    Convert camelCase to UPPER_SNAKE_CASE for XML keys.
    
    Args:
        camel_case_key (str): camelCase key
        
    Returns:
        str: UPPER_SNAKE_CASE key
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_key)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

def find_element_by_attributes(root, tag_name, attributes):
    """
    Find an XML element by tag name and attribute values.
    
    Args:
        root (Element): Root XML element
        tag_name (str): Tag name to search for
        attributes (dict): Attribute key-value pairs to match
        
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

def create_or_update_element(parent, tag_name, attributes):
    """
    Create or update an XML element with specified attributes.
    
    Args:
        parent (Element): Parent XML element
        tag_name (str): Tag name for the element
        attributes (dict): Attribute key-value pairs
        
    Returns:
        Element: Created or updated element
    """
    element = etree.SubElement(parent, tag_name)
    for attr, value in attributes.items():
        element.set(attr, str(value))
    return element

def xml_to_string(root, pretty_print=True):
    """
    Convert XML element to string with pretty printing.
    
    Args:
        root (Element): Root XML element
        pretty_print (bool): Whether to format with pretty printing
        
    Returns:
        str: XML string
    """
    # For ElementTree elements
    if isinstance(root, ET.Element):
        xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
        return format_xml_string(xml_str, pretty_print)
    
    # For lxml elements
    return etree.tostring(
        root, 
        encoding='utf-8', 
        xml_declaration=True,
        pretty_print=pretty_print
    ).decode('utf-8')

def format_xml_string(xml_str, pretty_print=True):
    """
    Format an XML string with proper indentation and line breaks.
    
    Args:
        xml_str (str): XML string to format
        pretty_print (bool): Whether to format with pretty printing
        
    Returns:
        str: Formatted XML string
    """
    if not pretty_print:
        return xml_str
    
    # Try to use lxml for better formatting
    try:
        # Parse the string into an lxml ElementTree
        root = etree.fromstring(xml_str.encode('utf-8'))
        # Format with lxml's pretty_print
        formatted_xml = etree.tostring(
            root,
            encoding='utf-8',
            pretty_print=True
        ).decode('utf-8')
        
        # Add XML declaration if needed
        if not formatted_xml.startswith('<?xml'):
            formatted_xml = '<?xml version="1.0" encoding="utf-8"?>\n' + formatted_xml
            
        return formatted_xml
    
    except Exception as e:
        # Fall back to minidom if lxml fails
        print(f"Warning: lxml formatting failed, falling back to minidom: {str(e)}")
        import xml.dom.minidom
        
        # Parse the XML string
        try:
            dom = xml.dom.minidom.parseString(xml_str)
            
            # Get pretty XML string with the xml declaration
            formatted_xml = dom.toprettyxml(indent='  ')
            
            # Remove empty lines
            lines = [line for line in formatted_xml.split('\n') if line.strip()]
            return '\n'.join(lines)
        except Exception as e2:
            print(f"Warning: XML formatting failed completely: {str(e2)}")
            # Return original if all else fails
            return xml_str

def format_timestamp(date_str):
    """
    Format a date string as a timestamp for the XML.
    
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD HH:MM:SS'
        
    Returns:
        str: Formatted timestamp string like "{ts '2025-04-02 16:36:52'}"
    """
    if not date_str:
        return None
    
    return f"{{ts '{date_str}'}}"

def validate_xml_against_schema(xml_string, schema_path):
    """
    Validate an XML string against an XSD schema.
    
    Args:
        xml_string (str): XML string to validate
        schema_path (str): Path to the XSD schema
        
    Returns:
        bool: True if valid, raises exception otherwise
    """
    try:
        schema_doc = etree.parse(schema_path)
        schema = etree.XMLSchema(schema_doc)
        
        xml_doc = etree.fromstring(xml_string.encode('utf-8'))
        schema.assertValid(xml_doc)
        return True
    except Exception as e:
        raise ValueError(f"XML validation failed: {str(e)}")

def fix_xml_structure(xml_string):
    """
    Fix common structural issues in XML files.
    
    Args:
        xml_string (str): Original XML string
        
    Returns:
        str: Corrected XML string
    """
    # Remove duplicate XML declarations
    xml_decl_pattern = re.compile(r'<\?xml[^>]*\?>')
    xml_decls = xml_decl_pattern.findall(xml_string)
    if len(xml_decls) > 1:
        for i in range(1, len(xml_decls)):
            xml_string = xml_string.replace(xml_decls[i], '')
    
    # Remove duplicate DataServices processing instructions
    ds_pattern = re.compile(r'<\?DataServices[^>]*\?>')
    ds_instrs = ds_pattern.findall(xml_string)
    if len(ds_instrs) > 1:
        for i in range(1, len(ds_instrs)):
            xml_string = xml_string.replace(ds_instrs[i], '')
    
    # Remove root tags if present
    xml_string = re.sub(r'<root>\s*', '', xml_string)
    xml_string = re.sub(r'\s*</root>', '', xml_string)
    
    # Fix TOPLEVEL tag if it's outside the export tag
    if '</TOPLEVEL>' in xml_string and '</export>' in xml_string:
        if xml_string.find('</TOPLEVEL>') > xml_string.find('</export>'):
            xml_string = xml_string.replace('</TOPLEVEL>', '')
            # Add it back inside export
            xml_string = xml_string.replace('</export>', '</export>')
    
    # Ensure there's a closing export tag
    if '<export>' in xml_string and '</export>' not in xml_string:
        xml_string += '\n</export>'
    
    # Try to format the result
    try:
        # Parse the corrected string
        root = etree.fromstring(xml_string.encode('utf-8'))
        # Get the formatted result
        result = etree.tostring(root, encoding='utf-8', pretty_print=True).decode('utf-8')
        
        # Add XML declaration
        if not result.startswith('<?xml'):
            result = '<?xml version="1.0" encoding="utf-8"?>\n' + result
        
        # Add DataServices PI if it was present
        if ds_instrs and not '<?DataServices' in result:
            result = result.replace('<?xml version="1.0" encoding="utf-8"?>\n', 
                                   '<?xml version="1.0" encoding="utf-8"?>\n' + ds_instrs[0] + '\n\n')
            
        return result
    except Exception as e:
        print(f"Warning: XML reformatting failed: {str(e)}")
        return xml_string