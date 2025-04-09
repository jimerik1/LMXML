# services/xml_methods/utils.py
from datetime import datetime
from utils.xml_helpers import format_timestamp

def add_creation_info(generator, elem):
    """
    Add creation and update info to an element.
    
    Args:
        generator: The XMLGenerator instance
        elem (Element): XML element
    """
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elem.set("CREATE_DATE", format_timestamp(now_str))
    elem.set("UPDATE_DATE", format_timestamp(now_str))
    elem.set("CREATE_USER_ID", "API_USER")
    elem.set("UPDATE_USER_ID", "API_USER")
    elem.set("CREATE_APP_ID", "XML_API")
    elem.set("UPDATE_APP_ID", "XML_API")