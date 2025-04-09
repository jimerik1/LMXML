# services/xml_methods/dls.py
from lxml import etree as ET
from services.xml_methods.utils import add_creation_info

def update_dls_overrides(generator, export_elem, dls_override_group):
    """
    Update dogleg severity overrides in the XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        dls_override_group (dict): DLS override group
    """
    if not dls_override_group:
        return
    
    # Get IDs
    well_ids = generator.id_registry.id_map.get('WELL', [])
    wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
    scenario_ids = generator.id_registry.id_map.get('SCENARIO', [])
    
    # Create group element
    group_elem = ET.SubElement(export_elem, "TU_DLS_OVERRIDE_GROUP")
    
    # Set attributes
    if 'groupId' in dls_override_group:
        group_elem.set("DLS_OVERRIDE_GROUP_ID", dls_override_group['groupId'])
    
    # Add well and wellbore IDs
    if wellbore_ids:
        group_elem.set("WELLBORE_ID", wellbore_ids[0])
        if well_ids:
            group_elem.set("WELL_ID", well_ids[0])
    
    # Add scenario ID if available
    if scenario_ids:
        group_elem.set("SCENARIO_ID", scenario_ids[0])
    
    # Add creation info
    add_creation_info(generator, group_elem)
    
    # Add overrides
    for override in dls_override_group.get('overrides', []):
        override_elem = ET.SubElement(export_elem, "TU_DLS_OVERRIDE")
        
        if 'overrideId' in override:
            override_elem.set("DLS_OVERRIDE_ID", override['overrideId'])
        
        override_elem.set("DLS_OVERRIDE_GROUP_ID", dls_override_group.get('groupId', ''))
        
        # Add well and wellbore IDs
        if wellbore_ids:
            override_elem.set("WELLBORE_ID", wellbore_ids[0])
            if well_ids:
                override_elem.set("WELL_ID", well_ids[0])
        
        # Add scenario ID if available
        if scenario_ids:
            override_elem.set("SCENARIO_ID", scenario_ids[0])
        
        # Set depth and severity values
        if 'topDepth' in override:
            override_elem.set("MD_TOP", str(override['topDepth']))
        if 'baseDepth' in override:
            override_elem.set("MD_BASE", str(override['baseDepth']))
        if 'doglegSeverity' in override:
            override_elem.set("DOGLEG_SEVERITY", str(override['doglegSeverity']))
        
        # Add creation and update info
        add_creation_info(generator, override_elem)