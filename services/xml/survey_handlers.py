# services/xml/survey_handlers.py
import logging
from typing import Dict, List, Any
from lxml import etree as ET

from services.xml.utils import generate_random_id
from services.xml.element_operations import create_element, remove_existing_elements

logger = logging.getLogger(__name__)

def update_survey_stations(root: ET.Element, well_id: str, wellbore_id: str, 
                          survey_header_id: str, survey_stations: List[Dict[str, Any]]) -> bool:
    """
    Update survey stations in the XML.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        survey_header_id: Survey header ID
        survey_stations: List of survey station data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Updating survey stations for header {survey_header_id}")
        
        # Remove existing survey station entries
        xpath = f".//CD_DEFINITIVE_SURVEY_STATION[@DEF_SURVEY_HEADER_ID='{survey_header_id}']"
        remove_existing_elements(root, xpath)
        
        # Find the survey header element
        header_xpath = f".//CD_DEFINITIVE_SURVEY_HEADER[@DEF_SURVEY_HEADER_ID='{survey_header_id}']"
        header_elements = root.xpath(header_xpath)
        
        if not header_elements:
            logger.warning(f"Survey header with ID {survey_header_id} not found")
            return False
        
        # Update the header name if provided
        if survey_stations and 'name' in survey_stations[0]:
            header_elements[0].set('NAME', survey_stations[0]['name'])
            logger.info(f"Updated survey header name to: {survey_stations[0]['name']}")
        
        # Get the header element and its parent
        header_elem = header_elements[0]
        parent_elem = header_elem.getparent()
        
        # Get the index of the header element in its parent's children
        header_index = parent_elem.index(header_elem)
        
        # Sort survey stations by MD in descending order (deepest first)
        sorted_stations = sorted(survey_stations, key=lambda x: float(x.get('md', 0)), reverse=True)
        
        # Add new survey station elements
        for i, station in enumerate(sorted_stations):
            # Generate a new ID for each station
            station_id = generate_random_id()
            
            # Create basic attributes dictionary
            attributes = {
                'WELL_ID': well_id,
                'WELLBORE_ID': wellbore_id,
                'DEF_SURVEY_HEADER_ID': survey_header_id,
                'DEFINITIVE_SURVEY_ID': station_id,
                'AZIMUTH': str(station.get('azimuth')),
                'INCLINATION': str(station.get('inclination')),
                'MD': str(station.get('md')),
                'SEQUENCE_NO': str(float(i)),
                'DATA_ENTRY_MODE': str(station.get('dataEntryMode', '0'))
            }
            
            # Add optional attributes if provided
            if 'tvd' in station:
                attributes['TVD'] = str(station['tvd'])
            if 'doglegSeverity' in station:
                attributes['DOGLEG_SEVERITY'] = str(station['doglegSeverity'])
            
            # Create the element
            element = create_element('CD_DEFINITIVE_SURVEY_STATION', attributes)
            
            # Insert the element
            parent_elem.insert(header_index + 1 + i, element)
            
            logger.info(f"Added survey station at MD {station.get('md')}: "
                       f"AZ={station.get('azimuth')}, INC={station.get('inclination')}")
        
        logger.info("Survey stations update completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating survey stations: {str(e)}", exc_info=True)
        return False