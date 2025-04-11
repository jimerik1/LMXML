# services/xml_methods/scenario.py
from lxml import etree as ET
from utils.xml_helpers import set_attributes_ordered
from services.xml_methods.utils import add_creation_info

def add_scenario_element(generator, export_elem):
    """
    Add scenario element to link different components together.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
    """
    # Get IDs
    well_ids = generator.id_registry.id_map.get('WELL', [])
    wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
    scenario_ids = generator.id_registry.id_map.get('SCENARIO', [])
    temp_group_ids = generator.id_registry.id_map.get('TEMP_GRADIENT_GROUP', [])
    pore_group_ids = generator.id_registry.id_map.get('PORE_PRESSURE_GROUP', [])
    frac_group_ids = generator.id_registry.id_map.get('FRAC_GRADIENT_GROUP', [])
    survey_header_ids = generator.id_registry.id_map.get('SURVEY_HEADER', [])
    datum_ids = generator.id_registry.id_map.get('DATUM', [])
    
    # Skip if no scenario ID or required relationships
    if not scenario_ids or not wellbore_ids or not well_ids:
        return
    
    # Prepare attributes for scenario element
    attributes = {
        "WELL_ID": well_ids[0],
        "WELLBORE_ID": wellbore_ids[0],
        "SCENARIO_ID": scenario_ids[0],
        "PHASE": "PROTOTYPE"
    }
    
    # Set related IDs if available
    if datum_ids:
        attributes["DATUM_ID"] = datum_ids[0]
        attributes["ORIGINAL_TUBULAR_DATUM_ID"] = datum_ids[0]
    
    if temp_group_ids:
        attributes["TEMP_GRADIENT_GROUP_ID"] = temp_group_ids[0]
    
    if pore_group_ids:
        attributes["PORE_PRESSURE_GROUP_ID"] = pore_group_ids[0]
    
    if frac_group_ids:
        attributes["FRAC_GRADIENT_GROUP_ID"] = frac_group_ids[0]
    
    if survey_header_ids:
        attributes["DEF_SURVEY_HEADER_ID"] = survey_header_ids[0]
    
    # Set name from well info if available
    well_data = generator.id_registry.get_entity_data('WELL', well_ids[0])
    if well_data and 'wellCommonName' in well_data:
        attributes["NAME"] = well_data['wellCommonName']
    else:
        # Use a default name
        attributes["NAME"] = "Scenario"
    
    # Create scenario element
    scenario_elem = ET.SubElement(export_elem, "CD_SCENARIO")
    set_attributes_ordered(scenario_elem, attributes)
    
    # Add creation info
    add_creation_info(generator, scenario_elem)
    
    # Add case elements for each assembly
    add_case_elements(generator, export_elem)

def add_case_elements(generator, export_elem):
    """
    Add case elements to link scenarios to assemblies.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
    """
    # Get IDs
    scenario_ids = generator.id_registry.id_map.get('SCENARIO', [])
    assembly_ids = generator.id_registry.id_map.get('ASSEMBLY', [])
    well_ids = generator.id_registry.id_map.get('WELL', [])
    wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
    case_ids = generator.id_registry.id_map.get('CASE', [])
    
    # Skip if no required IDs
    if not scenario_ids or not assembly_ids or not case_ids:
        return
    
    # Check if we already have CD_CASE elements to avoid duplication
    existing_cases = export_elem.findall("./CD_CASE")
    if existing_cases:
        # If we already have case elements, don't add more
        return
    
    # Get relationships between cases, scenarios and assemblies
    for i, case_id in enumerate(case_ids):
        # Get related assembly
        assembly_id = None
        for (e_type, e_id, c_type), child_ids in generator.id_registry.relationship_map.items():
            if e_type == 'ASSEMBLY' and c_type == 'CASE' and case_id in child_ids:
                assembly_id = e_id
                break
        
        # Skip if no assembly relationship found
        if not assembly_id:
            continue
        
        # Set case name from assembly
        assembly_data = generator.id_registry.get_entity_data('ASSEMBLY', assembly_id)
        if assembly_data and 'assemblyName' in assembly_data:
            case_name = assembly_data['assemblyName']
        else:
            case_name = f"Case {i+1}"
        
        # Prepare attributes for case element
        attributes = {
            "WELL_ID": well_ids[0] if well_ids else "",
            "WELLBORE_ID": wellbore_ids[0] if wellbore_ids else "",
            "CASE_ID": case_id,
            "SCENARIO_ID": scenario_ids[0],
            "ASSEMBLY_ID": assembly_id,
            "IS_LINKED": "Y",
            "SEQUENCE_NO": str(float(i)),
            "CASE_NAME": case_name
        }
        
        # Create case element
        case_elem = ET.SubElement(export_elem, "CD_CASE")
        set_attributes_ordered(case_elem, attributes)
        
        # Add creation info
        add_creation_info(generator, case_elem)