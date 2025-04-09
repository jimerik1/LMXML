# services/xml_methods/datum.py
from lxml import etree as ET
from utils.xml_helpers import convert_camel_to_xml_key
from services.xml_methods.utils import add_creation_info

def update_datum(generator, export_elem, datum):
    """
    Update datum information in the XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        datum (dict): Datum information
    """
    if not datum:
        return
    
    # Get well IDs
    well_ids = generator.id_registry.id_map.get('WELL', [])
    
    # Create datum element
    datum_elem = ET.SubElement(export_elem, "CD_DATUM")
    
    # Set attributes
    if 'datumId' in datum:
        datum_elem.set("DATUM_ID", datum['datumId'])
    
    # Set well ID
    if well_ids:
        datum_elem.set("WELL_ID", well_ids[0])
    elif 'wellId' in datum:
        datum_elem.set("WELL_ID", datum['wellId'])
    
    # Set other attributes
    for key, value in datum.items():
        if key not in ['datumId', 'wellId']:
            xml_key = convert_camel_to_xml_key(key)
            datum_elem.set(xml_key, str(value))
    
    # Add creation info
    add_creation_info(generator, datum_elem)