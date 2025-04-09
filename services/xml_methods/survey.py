# services/xml_methods/survey.py
from lxml import etree as ET
from utils.xml_helpers import convert_camel_to_xml_key
from services.xml_methods.utils import add_creation_info

def update_survey_header(generator, export_elem, survey_header):
    """
    Update survey header and stations in the XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        survey_header (dict): Survey header
    """
    if not survey_header:
        return
    
    # Get IDs
    well_ids = generator.id_registry.id_map.get('WELL', [])
    wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
    
    # Create header element
    header_elem = ET.SubElement(export_elem, "CD_DEFINITIVE_SURVEY_HEADER")
    
    # Set attributes
    if 'headerId' in survey_header:
        header_elem.set("DEF_SURVEY_HEADER_ID", survey_header['headerId'])
    
    # Set well and wellbore IDs
    if wellbore_ids:
        header_elem.set("WELLBORE_ID", wellbore_ids[0])
        if well_ids:
            header_elem.set("WELL_ID", well_ids[0])
    
    # Set other attributes
    for key, value in survey_header.items():
        if key not in ['headerId', 'wellboreId', 'stations']:
            xml_key = convert_camel_to_xml_key(key)
            header_elem.set(xml_key, str(value))
    
    # Add phase if missing
    if 'PHASE' not in header_elem.attrib:
        header_elem.set("PHASE", "PROTOTYPE")
    
    # Add creation info
    add_creation_info(generator, header_elem)
    
    # Add survey stations
    for station in survey_header.get('stations', []):
        station_elem = ET.SubElement(export_elem, "CD_DEFINITIVE_SURVEY_STATION")
        
        if 'stationId' in station:
            station_elem.set("DEFINITIVE_SURVEY_ID", station['stationId'])
        
        # Link to header
        station_elem.set("DEF_SURVEY_HEADER_ID", survey_header.get('headerId', ''))
        
        # Set station attributes
        for key, value in station.items():
            if key != 'stationId':
                xml_key = convert_camel_to_xml_key(key)
                station_elem.set(xml_key, str(value))