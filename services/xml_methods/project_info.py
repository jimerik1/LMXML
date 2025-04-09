# services/xml_methods/project_info.py
from lxml import etree as ET
from utils.xml_helpers import convert_camel_to_xml_key
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
        site_elem = ET.SubElement(export_elem, "CD_SITE")
        
        # Set attributes
        for key, value in project_info['site'].items():
            if key == 'siteId':
                site_elem.set("SITE_ID", value)
            else:
                xml_key = convert_camel_to_xml_key(key)
                site_elem.set(xml_key, str(value))
        
        # Add tight group reference if not present
        if 'TIGHT_GROUP_ID' not in site_elem.attrib:
            site_elem.set("TIGHT_GROUP_ID", "T0001")
        
        # Add creation and update info
        add_creation_info(generator, site_elem)
    
    # Update well information
    if 'well' in project_info:
        well_elem = ET.SubElement(export_elem, "CD_WELL")
        
        # Set attributes
        for key, value in project_info['well'].items():
            if key == 'wellId':
                well_elem.set("WELL_ID", value)
            elif key == 'siteId':
                well_elem.set("SITE_ID", value)
            elif key == 'isOffshore':
                # Convert to Y/N format
                well_elem.set("IS_OFFSHORE", "Y" if str(value).upper() in ['Y', 'YES', 'TRUE', '1'] else "N")
            else:
                xml_key = convert_camel_to_xml_key(key)
                well_elem.set(xml_key, str(value))
        
        # Add tight group reference if not present
        if 'TIGHT_GROUP_ID' not in well_elem.attrib:
            well_elem.set("TIGHT_GROUP_ID", "T0001")
        
        # Add creation and update info
        add_creation_info(generator, well_elem)
    
    # Update wellbore information
    if 'wellbore' in project_info:
        wellbore_elem = ET.SubElement(export_elem, "CD_WELLBORE")
        
        # Set attributes
        for key, value in project_info['wellbore'].items():
            if key == 'wellboreId':
                wellbore_elem.set("WELLBORE_ID", value)
            elif key == 'wellId':
                wellbore_elem.set("WELL_ID", value)
            elif key == 'isActive':
                # Convert to Y/N format
                wellbore_elem.set("IS_ACTIVE", "Y" if str(value).upper() in ['Y', 'YES', 'TRUE', '1'] else "N")
            elif key == 'wellboreType':
                # Set wellbore type
                wellbore_elem.set("WELLBORE_TYPE", str(value))
            else:
                xml_key = convert_camel_to_xml_key(key)
                wellbore_elem.set(xml_key, str(value))
        
        # Add creation and update info
        add_creation_info(generator, wellbore_elem)