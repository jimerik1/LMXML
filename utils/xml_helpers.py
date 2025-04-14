# utils/xml_helpers.py
import xml.etree.ElementTree as ET
import re
from lxml import etree

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

def set_attributes_ordered(element, attributes):
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
    set_attributes_ordered(element, attributes)
    return element

def xml_to_string(root, pretty_print=True):
    """
    Convert XML element to string with pretty printing and ensure line breaks between elements.
    
    Args:
        root (Element): Root XML element
        pretty_print (bool): Whether to format with pretty printing
        
    Returns:
        str: XML string
    """
    # For ElementTree elements
    if isinstance(root, ET.Element):
        xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
    else:
        # For lxml elements
        xml_str = etree.tostring(
            root, 
            encoding='utf-8', 
            xml_declaration=True,
            pretty_print=pretty_print
        ).decode('utf-8')
    
    # Apply line breaks between elements (even if pretty_print didn't work)
    xml_str = re.sub(r'><', '>\n<', xml_str)
    
    # Fix XML declaration if needed
    if '<?DataServices' not in xml_str:
        xml_str = xml_str.replace('<?xml version=\'1.0\' encoding=\'utf-8\'?>', 
            '<?xml version="1.0" standalone="no"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>')
        xml_str = xml_str.replace('<?xml version="1.0" encoding="utf-8"?>', 
            '<?xml version="1.0" standalone="no"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>')
    
    return xml_str

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
            formatted_xml = '<?xml version="1.0" standalone="no"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>\n' + formatted_xml
            
        return formatted_xml
    
    except Exception as e:
        # Fall back to a manual approach if lxml fails
        print(f"Warning: lxml formatting failed, falling back to manual formatting: {str(e)}")
        
        # Add line breaks after each closing tag, except for self-closing tags
        xml_str = re.sub(r'(</[^>]+>)(?![\s\n])', r'\1\n', xml_str)
        
        # Add line breaks after opening tags that aren't followed by closing tags or other opening tags
        xml_str = re.sub(r'(<[^/][^>]*[^/]>)(?![\s\n<])', r'\1\n', xml_str)
        
        # Add line breaks after self-closing tags
        xml_str = re.sub(r'(<[^>]+/>)(?![\s\n])', r'\1\n', xml_str)
        
        # Clean up extra line breaks to avoid too many blank lines
        xml_str = re.sub(r'\n\s*\n', '\n', xml_str)
        
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
    Fix common structural issues in XML files and ensure proper formatting.
    
    Args:
        xml_string (str): Original XML string
        
    Returns:
        str: Corrected XML string with each element on its own line
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
    
    # Helper function to ensure elements are on new lines with proper indentation
    def ensure_elements_on_new_lines(xml_str):
        """Helper function to ensure elements are on new lines with proper indentation."""
        # Add a newline after each closing tag if not already present
        xml_str = re.sub(r'(</[^>]+>)(?![\s\n])', r'\1\n', xml_str)
        
        # Add a newline after each opening tag that isn't immediately followed by text or another tag
        xml_str = re.sub(r'(<[^/][^>]*[^/]>)(?![\s\n<])', r'\1\n', xml_str)
        
        # Add a newline after self-closing tags
        xml_str = re.sub(r'(<[^>]+/>)(?![\s\n])', r'\1\n', xml_str)
        
        # Replace multiple newlines with a single newline
        xml_str = re.sub(r'\n+', '\n', xml_str)
        
        # Add proper indentation
        lines = xml_str.split('\n')
        indent_level = 0
        result_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if the line is a closing tag
            if line.startswith('</'):
                indent_level = max(0, indent_level - 1)
            
            # Add the indented line
            result_lines.append('  ' * indent_level + line)
            
            # Check if the line is an opening tag and not a self-closing tag
            if '<' in line and '>' in line and not (line.startswith('<?') or '/>' in line or '</' in line):
                indent_level += 1
        
        return '\n'.join(result_lines)
    
    # Try to format the result using lxml
    try:
        # Parse the corrected string
        root = etree.fromstring(xml_string.encode('utf-8'))
        # Get the formatted result
        result = etree.tostring(root, encoding='utf-8', pretty_print=True).decode('utf-8')
        
        # Add XML declaration
        if not result.startswith('<?xml'):
            result = '<?xml version="1.0" encoding="utf-8"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>\n' + result
        
        # Add DataServices PI if it was present
        if ds_instrs and '<?DataServices' not in result:
            result = result.replace('<?xml version="1.0" encoding="utf-8"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>\n', 
                                   '<?xml version="1.0" encoding="utf-8"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>\n' + ds_instrs[0] + '\n\n')
        
        # Ensure elements are on new lines with proper formatting
        result = ensure_elements_on_new_lines(result)
        
        return result
    except Exception as e:
        print(f"Warning: XML reformatting failed: {str(e)}")
        # If lxml formatting fails, try the manual approach
        return ensure_elements_on_new_lines(xml_string)