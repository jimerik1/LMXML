# services/xml_methods/core.py
import os
from lxml import etree as ET
from services.id_registry import IDRegistry
from utils.xml_helpers import load_xml_template, xml_to_string, fix_xml_structure

def initialize(generator, base_template_path):
    """
    Initialize the XML generator with a template path.
    
    Args:
        generator: The XMLGenerator instance
        base_template_path (str): Path to the base XML template
    """
    generator.base_template_path = base_template_path
    generator.id_registry = IDRegistry()
    
    # Get the template directory path from the base template path
    generator.template_dir = os.path.dirname(base_template_path)
    
    # Set the binary data library path
    generator.binary_data_path = os.path.join(generator.template_dir, 'binary_data_library.xml')

def generate_xml(generator, payload):
    """
    Generate XML from a structured payload by updating the template.
    
    Args:
        generator: The XMLGenerator instance
        payload (dict): Structured data payload
        
    Returns:
        str: Generated XML as a string
    """
    # Load the template
    tree = load_xml_template(generator.base_template_path)
    root = tree.getroot()
    
    # Check if there's a 'root' element that needs to be removed (keeping its children)
    if root.tag == 'root':
        # Create a new root element for 'export'
        new_root = ET.Element('export')
        # Add all children of the old root to the new root
        for child in root:
            if child.tag == 'export':
                # If there's already an export element, use its children directly
                for export_child in child:
                    new_root.append(export_child)
            else:
                new_root.append(child)
        # Replace the old root with the new one
        root = new_root
        tree._setroot(root)
    
    # Find the export element (which should now be the root)
    if root.tag == 'export':
        export_elem = root
    else:
        export_elem = root.find(".//export")
        if export_elem is None:
            # Create export element if not found
            export_elem = ET.SubElement(root, "export")
    
    # Add TOPLEVEL section if missing
    toplevel_elem = export_elem.find("./TOPLEVEL")
    if toplevel_elem is None:
        toplevel_elem = ET.SubElement(export_elem, "TOPLEVEL")
        # Add standard geodetic elements based on the payload
        geo_system = ET.SubElement(toplevel_elem, "CD_GEO_SYSTEM")
        geo_system.set("GEO_SYSTEM_ID", "EPE Onshore NL")
        geo_system.set("GEO_DATUM_ID", "AMERSFOORT")
        geo_system.set("MEASURE_ID", "121.0")
        geo_system.set("GEO_SYSTEM_NAME", "EPE Onshore NL")
        
        geo_zone = ET.SubElement(toplevel_elem, "CD_GEO_ZONE")
        geo_zone.set("GEO_SYSTEM_ID", "EPE Onshore NL")
        geo_zone.set("GEO_ZONE_ID", "RD New")
        geo_zone.set("ZONE_NAME", "Amersfoort / RD New [1672_28992]")
        geo_zone.set("LAT_ORIGIN", "52.1561605")
        geo_zone.set("LON_ORIGIN", "5.3876388")
        geo_zone.set("SCALE_FACTOR", "0.9999079")
        geo_zone.set("FALSE_EASTING", "155000.0")
        geo_zone.set("FALSE_NORTHING", "463000.0")
        geo_zone.set("PROJ_TYPE", "29.0")
        
        geo_datum = ET.SubElement(toplevel_elem, "CD_GEO_DATUM")
        geo_datum.set("GEO_DATUM_ID", "AMERSFOORT")
        geo_datum.set("DATUM_NAME", "Amersfoort [1672_4289]")
        geo_datum.set("GEO_ELLIPSOID_ID", "BESSEL 1841")
        geo_datum.set("PMSHIFT", "0.0")
        geo_datum.set("X_SHIFT", "565.04")
        geo_datum.set("Y_SHIFT", "49.91")
        geo_datum.set("Z_SHIFT", "465.84")
        geo_datum.set("X_ROTATE", "-0.4094")
        geo_datum.set("Y_ROTATE", "0.3597")
        geo_datum.set("Z_ROTATE", "-1.8685")
        geo_datum.set("SCALE_FACTOR", "4.0772")
        
        geo_ellipsoid = ET.SubElement(toplevel_elem, "CD_GEO_ELLIPSOID")
        geo_ellipsoid.set("GEO_ELLIPSOID_ID", "BESSEL 1841")
        geo_ellipsoid.set("NAME", "Bessel 1841")
        geo_ellipsoid.set("SEMI_MAJOR", "6377397.155")
        geo_ellipsoid.set("FIRST_ECCENTRICITY", "0.0816968312204014")
    
    # Add tight group section if missing
    tight_group_elem = export_elem.find("./MD_SITE_TIGHT_GROUP")
    if tight_group_elem is None:
        tight_group_elem = ET.SubElement(export_elem, "MD_SITE_TIGHT_GROUP")
        tight_group_elem.set("TIGHT_GROUP_ID", "T0001")
        tight_group_elem.set("TIGHT_GROUP_NAME", "UNRESTRICTED")
        tight_group_elem.set("DESCRIPTION", "Unrestricted")
    
    # Add policy section if missing - essential for references
    policy_elem = export_elem.find("./CD_POLICY")
    if policy_elem is None:
        policy_elem = ET.SubElement(export_elem, "CD_POLICY")
        policy_elem.set("CUSTOMER_NAME", "CONCEPT WELL PLANNING - NL")
        policy_elem.set("POLICY_ID", "Pzrgw9f4JC")  # Keep consistent with binary data
        policy_elem.set("CUSTOMER_REPRESENTATIVE", "Application Support")
        policy_elem.set("CUSTOMER_TELEPHONE", "SSW-Support-UI-E@shell.com")
        policy_elem.set("IS_READONLY", "Y")
        policy_elem.set("REPORTING_TIME", "{ts '1970-01-01 00:00:00'}")
        policy_elem.set("CREATE_DATE", "{ts '2008-09-28 18:23:05'}")
        policy_elem.set("CREATE_USER_ID", "API_USER")
        policy_elem.set("CREATE_APP_ID", "XML_API")
        policy_elem.set("UPDATE_DATE", "{ts '2025-04-02 16:36:52'}")
        policy_elem.set("UPDATE_USER_ID", "API_USER")
        policy_elem.set("UPDATE_APP_ID", "XML_API")
        policy_elem.set("BA_CODE", "GL")
    
    # Generate and register IDs as needed
    generator._prepare_ids(payload)
    
    # Clear existing elements that will be replaced
    generator._clear_template_elements(export_elem, payload)
    
    # Update project information first (site, well, wellbore)
    generator._update_project_info(export_elem, payload.get('projectInfo', {}))
    
    # Add scenario element right after project info
    generator._add_scenario_element(export_elem)
    
    # Update DLS overrides
    if 'formationInputs' in payload and 'dlsOverrideGroup' in payload['formationInputs']:
        generator._update_dls_overrides(export_elem, payload['formationInputs']['dlsOverrideGroup'])
    
    # Update assembly information
    generator._update_casing_schematics(export_elem, payload.get('casingSchematics', {}))
    
    # Update survey header and stations
    if 'formationInputs' in payload and 'surveyHeader' in payload['formationInputs']:
        generator._update_survey_header(export_elem, payload['formationInputs']['surveyHeader'])
    
    # Update formation inputs (temperature, pressure profiles)
    generator._update_formation_inputs(export_elem, payload.get('formationInputs', {}))
    
    # Update datum
    if 'datum' in payload:
        generator._update_datum(export_elem, payload['datum'])
    
    # Add case elements linking scenarios to assemblies
    generator._add_case_elements(export_elem)
    
    # Validate relationships
    validation_errors = generator.id_registry.validate_references()
    if validation_errors:
        raise ValueError("\n".join(validation_errors))
    
    # Inject binary data from binary_data_library.xml if it exists
    generator._inject_binary_data(export_elem)
    
    # Get XML as string
    xml_string = xml_to_string(root)
    
    # Fix formatting and structure issues
    xml_string = fix_xml_structure(xml_string)
    
    return xml_string