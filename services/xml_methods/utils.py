# services/xml_methods/utils.py
from datetime import datetime
from utils.xml_helpers import format_timestamp, set_attributes_ordered

def add_creation_info(generator, elem):
    """
    Add creation and update info to an element.
    
    Args:
        generator: The XMLGenerator instance
        elem (Element): XML element
    """
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    attributes = {
        "CREATE_DATE": format_timestamp(now_str),
        "UPDATE_DATE": format_timestamp(now_str),
        "CREATE_USER_ID": "API_USER",
        "UPDATE_USER_ID": "API_USER",
        "CREATE_APP_ID": "XML_API",
        "UPDATE_APP_ID": "XML_API"
    }
    
    # Use set_attributes_ordered to maintain consistent order
    set_attributes_ordered(elem, attributes)