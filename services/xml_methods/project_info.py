# services/xml_methods/project_info.py
from lxml import etree as ET
from utils.xml_helpers import convert_camel_to_xml_key, set_attributes_ordered
from services.xml_methods.utils import add_creation_info

def update_project_info(generator, export_elem, project_info):
    """
    Update project information in the XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        project_info (dict): Project information
    """
    if not project_info:
        return
    
    # Update site information
    if 'site' in project_info:
        # Prepare attributes
        attributes = {}
        
        for key, value in project_info['site'].items():
            if key == 'siteId':
                attributes["SITE_ID"] = value
            else:
                xml_key = convert_camel_to_xml_key(key)
                attributes[xml_key] = str(value)
        
        # Add tight group reference if not present
        if 'TIGHT_GROUP_ID' not in attributes:
            attributes["TIGHT_GROUP_ID"] = "T0001"
        
        # Create site element
        site_elem = ET.SubElement(export_elem, "CD_SITE")
        set_attributes_ordered(site_elem, attributes)
        
        # Add creation and update info
        add_creation_info(generator, site_elem)
    
    # Update well information
    if 'well' in project_info:
        # Prepare attributes
        attributes = {}
        
        for key, value in project_info['well'].items():
            if key == 'wellId':
                attributes["WELL_ID"] = value
            elif key == 'siteId':
                attributes["SITE_ID"] = value
            elif key == 'isOffshore':
                # Convert to Y/N format
                attributes["IS_OFFSHORE"] = "Y" if str(value).upper() in ['Y', 'YES', 'TRUE', '1'] else "N"
            else:
                xml_key = convert_camel_to_xml_key(key)
                attributes[xml_key] = str(value)
        
        # Add tight group reference if not present
        if 'TIGHT_GROUP_ID' not in attributes:
            attributes["TIGHT_GROUP_ID"] = "T0001"
        
        # Create well element
        well_elem = ET.SubElement(export_elem, "CD_WELL")
        set_attributes_ordered(well_elem, attributes)
        
        # Add creation and update info
        add_creation_info(generator, well_elem)
    
    # Update wellbore information
    if 'wellbore' in project_info:
        # Prepare attributes
        attributes = {}
        
        for key, value in project_info['wellbore'].items():
            if key == 'wellboreId':
                attributes["WELLBORE_ID"] = value
            elif key == 'wellId':
                attributes["WELL_ID"] = value
            elif key == 'isActive':
                # Convert to Y/N format
                attributes["IS_ACTIVE"] = "Y" if str(value).upper() in ['Y', 'YES', 'TRUE', '1'] else "N"
            elif key == 'wellboreType':
                # Set wellbore type
                attributes["WELLBORE_TYPE"] = str(value)
            else:
                xml_key = convert_camel_to_xml_key(key)
                attributes[xml_key] = str(value)
        
        # Create wellbore element
        wellbore_elem = ET.SubElement(export_elem, "CD_WELLBORE")
        set_attributes_ordered(wellbore_elem, attributes)
        
        # Add creation and update info
        add_creation_info(generator, wellbore_elem)