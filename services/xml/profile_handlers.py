# services/xml/profile_handlers.py
import logging
from typing import Dict, List, Any, Optional, Tuple
from lxml import etree as ET

from services.xml.utils import generate_random_id, calculate_emw, format_xpath
from services.xml.element_operations import create_element, remove_existing_elements, find_group_element

logger = logging.getLogger(__name__)

def update_temperature_profiles(root: ET.Element, well_id: str, wellbore_id: str, 
                               temp_group_id: str, temp_profiles: List[Dict[str, Any]]) -> bool:
    """
    Update temperature profiles in the XML.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        temp_group_id: Temperature gradient group ID
        temp_profiles: List of temperature profile data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Updating temperature profiles for group {temp_group_id}")
        
        # Remove existing temperature gradient entries
        remove_existing_elements(root, f".//CD_TEMP_GRADIENT[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']")
        
        # Update surface temperature in the group if provided
        surface_temp = next((profile.get('temperature') for profile in temp_profiles 
                            if profile.get('depth') == 0), None)
        
        if surface_temp is not None:
            xpath = format_xpath('CD_TEMP_GRADIENT_GROUP', 'TEMP_GRADIENT_GROUP_ID', temp_group_id)
            elements = root.xpath(xpath)
            if elements:
                elements[0].set('SURFACE_AMBIENT_TEMP', str(surface_temp))
                logger.info(f"Updated surface temperature to {surface_temp}")
        
        # Find the temperature gradient group
        group_result = find_group_element(
            root,
            f".//CD_TEMP_GRADIENT_GROUP[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']",
            temp_group_id
        )
        
        if not group_result:
            return False
        
        group_elem, parent_elem, group_index = group_result
        
        # Filter profiles with depth > 0 and sort by depth in descending order (deepest first)
        depth_profiles = [p for p in temp_profiles if p.get('depth', 0) > 0]
        depth_profiles.sort(key=lambda x: x.get('depth', 0), reverse=True)
        
        # Add temperature profiles directly after the group element
        for i, profile in enumerate(depth_profiles):
            # Generate a new ID for each gradient element
            temp_id = generate_random_id()
            
            # Create element attributes
            element_attrs = {
                'WELL_ID': well_id,
                'WELLBORE_ID': wellbore_id,
                'TEMP_GRADIENT_GROUP_ID': temp_group_id,
                'TEMP_GRADIENT_ID': temp_id,
                'TEMPERATURE': str(profile.get('temperature')),
                'TVD': str(profile.get('depth'))
            }
            
            # Create the element
            element = create_element('CD_TEMP_GRADIENT', element_attrs)
            
            # Insert the element right after the group element
            parent_elem.insert(group_index + 1 + i, element)
            
            logger.info(f"Added temperature gradient at depth {profile.get('depth')}: {profile.get('temperature')}°F")
        
        return True
    except Exception as e:
        logger.error(f"Error updating temperature profiles: {str(e)}", exc_info=True)
        return False

def update_pressure_profiles(root: ET.Element, well_id: str, wellbore_id: str, pore_group_id: str, 
                            frac_group_id: str, pressure_profiles: List[Dict[str, Any]]) -> bool:
    """
    Update pressure profiles in the XML.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        pore_group_id: Pore pressure group ID
        frac_group_id: Frac gradient group ID
        pressure_profiles: List of pressure profile data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Updating pressure profiles")
        
        # Remove existing pressure entries for both pore and frac
        remove_existing_elements(root, ".//CD_PORE_PRESSURE")
        remove_existing_elements(root, ".//CD_FRAC_GRADIENT")
        
        # Group pressure profiles by type
        pore_pressures = [p for p in pressure_profiles if p.get('pressureType', '') == 'Pore']
        frac_pressures = [p for p in pressure_profiles if p.get('pressureType', '') == 'Frac']
        
        # Sort pressure profiles by depth in descending order (deepest first)
        pore_pressures.sort(key=lambda x: x.get('depth', 0), reverse=True)
        frac_pressures.sort(key=lambda x: x.get('depth', 0), reverse=True)
        
        # Process pore pressures
        if pore_pressures:
            pore_group_result = find_group_element(
                root,
                f".//CD_PORE_PRESSURE_GROUP[@PORE_PRESSURE_GROUP_ID='{pore_group_id}']",
                pore_group_id
            )
            
            if pore_group_result:
                _, parent_elem, group_index = pore_group_result
                add_pore_pressure_elements(root, pore_pressures, well_id, wellbore_id, 
                                          pore_group_id, parent_elem, group_index)
            else:
                logger.warning(f"Pore pressure group with ID {pore_group_id} not found")
        
        # Process frac gradients
        if frac_pressures:
            frac_group_result = find_group_element(
                root,
                f".//CD_FRAC_GRADIENT_GROUP[@FRAC_GRADIENT_GROUP_ID='{frac_group_id}']",
                frac_group_id
            )
            
            if frac_group_result:
                _, parent_elem, group_index = frac_group_result
                add_frac_gradient_elements(root, frac_pressures, well_id, wellbore_id, 
                                          frac_group_id, parent_elem, group_index)
            else:
                logger.warning(f"Frac gradient group with ID {frac_group_id} not found")
        
        return True
    except Exception as e:
        logger.error(f"Error updating pressure profiles: {str(e)}", exc_info=True)
        return False

def add_pore_pressure_elements(root: ET.Element, pressures: List[Dict[str, Any]], well_id: str, 
                              wellbore_id: str, group_id: str, parent_elem: ET.Element, 
                              start_index: int) -> None:
    """
    Add pore pressure elements to the XML.
    
    Args:
        root: Root XML element
        pressures: List of pressure profile data
        well_id: Well ID
        wellbore_id: Wellbore ID
        group_id: Pore pressure group ID
        parent_elem: Parent element to add to
        start_index: Starting index for insertion
    """
    for i, profile in enumerate(pressures):
        # Generate a new ID for each element
        pressure_id = generate_random_id()
        
        # Calculate EMW if not provided
        emw = profile.get('emw')
        if emw is None and profile.get('depth', 0) > 0:
            pressure = profile.get('pressure', 0)
            depth = profile.get('depth', 0)
            emw = calculate_emw(pressure, depth)
        
        # Create element attributes
        element_attrs = {
            'WELL_ID': well_id,
            'WELLBORE_ID': wellbore_id,
            'PORE_PRESSURE_GROUP_ID': group_id,
            'PORE_PRESSURE_ID': pressure_id,
            'PORE_PRESSURE': str(profile.get('pressure')),
            'TVD': str(profile.get('depth')),
            'IS_PERMEABLE_ZONE': 'Y',
            'PORE_PRESSURE_EMW': str(emw) if emw is not None else '0.0'
        }
        
        # Create the element
        element = create_element('CD_PORE_PRESSURE', element_attrs)
        
        # Insert the element
        parent_elem.insert(start_index + 1 + i, element)
        
        logger.info(f"Added pore pressure at depth {profile.get('depth')}: "
                   f"{profile.get('pressure')} {profile.get('units', 'psi')}")

def add_frac_gradient_elements(root: ET.Element, pressures: List[Dict[str, Any]], well_id: str, 
                              wellbore_id: str, group_id: str, parent_elem: ET.Element, 
                              start_index: int) -> None:
    """
    Add frac gradient elements to the XML.
    
    Args:
        root: Root XML element
        pressures: List of pressure profile data
        well_id: Well ID
        wellbore_id: Wellbore ID
        group_id: Frac gradient group ID
        parent_elem: Parent element to add to
        start_index: Starting index for insertion
    """
    for i, profile in enumerate(pressures):
        # Generate a new ID for each element
        gradient_id = generate_random_id()
        
        # Calculate EMW if not provided
        emw = profile.get('emw')
        if emw is None and profile.get('depth', 0) > 0:
            pressure = profile.get('pressure', 0)
            depth = profile.get('depth', 0)
            emw = calculate_emw(pressure, depth)
        
        # Create element attributes
        element_attrs = {
            'WELL_ID': well_id,
            'WELLBORE_ID': wellbore_id,
            'FRAC_GRADIENT_GROUP_ID': group_id,
            'FRAC_GRADIENT_ID': gradient_id,
            'FRAC_GRADIENT_PRESSURE': str(profile.get('pressure')),
            'TVD': str(profile.get('depth')),
            'FRAC_GRADIENT_EMW': str(emw) if emw is not None else '0.0'
        }
        
        # Create the element
        element = create_element('CD_FRAC_GRADIENT', element_attrs)
        
        # Insert the element
        parent_elem.insert(start_index + 1 + i, element)
        
        logger.info(f"Added frac gradient at depth {profile.get('depth')}: "
                   f"{profile.get('pressure')} {profile.get('units', 'psi')}")