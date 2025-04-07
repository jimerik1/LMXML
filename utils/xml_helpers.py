# XML manipulation utilities
import xml.etree.ElementTree as ET
import re

def load_xml_template(template_path):
    """Load an XML template from a file path."""
    try:
        return ET.parse(template_path)
    except Exception as e:
        raise Exception(f"Failed to load XML template: {str(e)}")

def convert_camel_to_xml_key(camel_case_key):
    """Convert camelCase to UPPER_SNAKE_CASE for XML keys."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_key)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

def find_element_by_attributes(root, tag_name, attributes):
    """Find an XML element by tag name and attribute values."""
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
    """Create or update an XML element with specified attributes."""
    element = ET.SubElement(parent, tag_name)
    for attr, value in attributes.items():
        element.set(attr, str(value))
    return element

def xml_to_string(root):
    """Convert XML element to string with basic pretty printing."""
    import xml.dom.minidom
    xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
    return xml.dom.minidom.parseString(xml_str).toprettyxml()
