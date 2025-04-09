# services/xml_methods/ids.py
from services.id_registry import IDRegistry

def prepare_ids(generator, payload):
    """
    Generate and register IDs for entities in the payload.
    
    Args:
        generator: The XMLGenerator instance
        payload (dict): Structured data payload
    """
    # Clear existing IDs to ensure fresh generation
    generator.id_registry = IDRegistry()
    
    # Project info IDs
    project_info = payload.get('projectInfo', {})
    
    # Site ID
    site = project_info.get('site', {})
    if site and not site.get('siteId'):
        site['siteId'] = generator.id_registry.generate_id('SITE')
    elif site and site.get('siteId'):
        generator.id_registry.register_entity('SITE', site['siteId'], site)
    
    # Well ID
    well = project_info.get('well', {})
    if well and not well.get('wellId'):
        well['wellId'] = generator.id_registry.generate_id('WELL')
    elif well and well.get('wellId'):
        generator.id_registry.register_entity('WELL', well['wellId'], well)
    
    # Register site-well relationship
    if site and well and site.get('siteId') and well.get('wellId'):
        generator.id_registry.register_relationship('SITE', site['siteId'], 'WELL', well['wellId'])
    
    # Wellbore ID
    wellbore = project_info.get('wellbore', {})
    if wellbore and not wellbore.get('wellboreId'):
        wellbore['wellboreId'] = generator.id_registry.generate_id('WELLBORE')
    elif wellbore and wellbore.get('wellboreId'):
        generator.id_registry.register_entity('WELLBORE', wellbore['wellboreId'], wellbore)
    
    # Register well-wellbore relationship
    if well and wellbore and well.get('wellId') and wellbore.get('wellboreId'):
        generator.id_registry.register_relationship('WELL', well['wellId'], 'WELLBORE', wellbore['wellboreId'])
    
    # Generate scenario ID if we have a well and wellbore
    if well and wellbore:
        scenario_id = generator.id_registry.generate_id('SCENARIO')
        generator.id_registry.register_entity('SCENARIO', scenario_id, 
                                           {'name': well.get('wellCommonName', 'Scenario')})
        generator.id_registry.register_relationship('WELL', well['wellId'], 'SCENARIO', scenario_id)
        generator.id_registry.register_relationship('WELLBORE', wellbore['wellboreId'], 'SCENARIO', scenario_id)
    
    # Handle DLS overrides
    formation_inputs = payload.get('formationInputs', {})
    dls_group = formation_inputs.get('dlsOverrideGroup', {})
    if dls_group:
        if not dls_group.get('groupId'):
            dls_group['groupId'] = generator.id_registry.generate_id('DLS_OVERRIDE_GROUP')
        else:
            generator.id_registry.register_entity('DLS_OVERRIDE_GROUP', dls_group['groupId'], dls_group)
        
        # Link to wellbore and scenario
        if wellbore and wellbore.get('wellboreId'):
            dls_group['wellboreId'] = wellbore['wellboreId']
            generator.id_registry.register_relationship(
                'WELLBORE', 
                wellbore['wellboreId'], 
                'DLS_OVERRIDE_GROUP', 
                dls_group['groupId']
            )
            
            # Link to scenario
            scenario_ids = generator.id_registry.id_map.get('SCENARIO', [])
            if scenario_ids:
                generator.id_registry.register_relationship(
                    'SCENARIO',
                    scenario_ids[0],
                    'DLS_OVERRIDE_GROUP',
                    dls_group['groupId']
                )
        
        # DLS override IDs
        for override in dls_group.get('overrides', []):
            if not override.get('overrideId'):
                override['overrideId'] = generator.id_registry.generate_id('DLS_OVERRIDE')
            else:
                generator.id_registry.register_entity('DLS_OVERRIDE', override['overrideId'], override)
            
            generator.id_registry.register_relationship(
                'DLS_OVERRIDE_GROUP', 
                dls_group['groupId'],
                'DLS_OVERRIDE', 
                override['overrideId']
            )
    
    # Handle survey header
    survey_header = formation_inputs.get('surveyHeader', {})
    if survey_header:
        if not survey_header.get('headerId'):
            survey_header['headerId'] = generator.id_registry.generate_id('SURVEY_HEADER')
        else:
            generator.id_registry.register_entity('SURVEY_HEADER', survey_header['headerId'], survey_header)
        
        # Link to wellbore
        if wellbore and wellbore.get('wellboreId'):
            survey_header['wellboreId'] = wellbore['wellboreId']
            generator.id_registry.register_relationship(
                'WELLBORE', 
                wellbore['wellboreId'],
                'SURVEY_HEADER', 
                survey_header['headerId']
            )
        
        # Survey station IDs
        for station in survey_header.get('stations', []):
            if not station.get('stationId'):
                station['stationId'] = generator.id_registry.generate_id('SURVEY_STATION')
            else:
                generator.id_registry.register_entity('SURVEY_STATION', station['stationId'], station)
            
            generator.id_registry.register_relationship(
                'SURVEY_HEADER', 
                survey_header['headerId'],
                'SURVEY_STATION', 
                station['stationId']
            )
    
    # Temperature gradient group ID
    if 'temperatureProfiles' in formation_inputs:
        temp_group_id = generator.id_registry.generate_id('TEMP_GRADIENT_GROUP')
        generator.id_registry.register_entity('TEMP_GRADIENT_GROUP', temp_group_id, {'name': 'Geothermal Gradient'})
        
        # Link to wellbore if available
        if wellbore and wellbore.get('wellboreId'):
            generator.id_registry.register_relationship(
                'WELLBORE',
                wellbore['wellboreId'],
                'TEMP_GRADIENT_GROUP',
                temp_group_id
            )
    
    # Pressure gradient group IDs
    if 'pressureProfiles' in formation_inputs:
        pore_group_id = generator.id_registry.generate_id('PORE_PRESSURE_GROUP')
        generator.id_registry.register_entity('PORE_PRESSURE_GROUP', pore_group_id, {'name': 'Pore Pressure'})
        
        frac_group_id = generator.id_registry.generate_id('FRAC_GRADIENT_GROUP')
        generator.id_registry.register_entity('FRAC_GRADIENT_GROUP', frac_group_id, {'name': 'Frac Gradient'})
        
        # Link to wellbore if available
        if wellbore and wellbore.get('wellboreId'):
            generator.id_registry.register_relationship(
                'WELLBORE',
                wellbore['wellboreId'],
                'PORE_PRESSURE_GROUP',
                pore_group_id
            )
            generator.id_registry.register_relationship(
                'WELLBORE',
                wellbore['wellboreId'],
                'FRAC_GRADIENT_GROUP',
                frac_group_id
            )
    
    # Datum ID
    datum = payload.get('datum', {})
    if datum:
        if not datum.get('datumId'):
            datum['datumId'] = generator.id_registry.generate_id('DATUM')
        else:
            generator.id_registry.register_entity('DATUM', datum['datumId'], datum)
        
        # Link to well
        if well and well.get('wellId'):
            datum['wellId'] = well['wellId']
            generator.id_registry.register_relationship(
                'WELL', 
                well['wellId'],
                'DATUM', 
                datum['datumId']
            )
    
    # Casing schematics IDs
    casing_schematics = payload.get('casingSchematics', {})
    
    # Material IDs
    materials = casing_schematics.get('materials', [])
    for material in materials:
        if not material.get('materialId'):
            material['materialId'] = generator.id_registry.generate_id('MATERIAL')
        else:
            generator.id_registry.register_entity('MATERIAL', material['materialId'], material)
    
    # Assembly IDs
    assemblies = casing_schematics.get('assemblies', [])
    for assembly in assemblies:
        if not assembly.get('assemblyId'):
            assembly['assemblyId'] = generator.id_registry.generate_id('ASSEMBLY')
        else:
            generator.id_registry.register_entity('ASSEMBLY', assembly['assemblyId'], assembly)
        
        # Link to wellbore if available
        if wellbore and wellbore.get('wellboreId'):
            assembly['wellboreId'] = wellbore['wellboreId']
            generator.id_registry.register_relationship(
                'WELLBORE', 
                wellbore['wellboreId'], 
                'ASSEMBLY', 
                assembly['assemblyId']
            )
        
        # Component IDs
        components = assembly.get('components', [])
        for component in components:
            if not component.get('componentId'):
                component['componentId'] = generator.id_registry.generate_id('ASSEMBLY_COMP')
            else:
                generator.id_registry.register_entity('ASSEMBLY_COMP', component['componentId'], component)
            
            # Register assembly-component relationship
            if assembly.get('assemblyId') and component.get('componentId'):
                generator.id_registry.register_relationship(
                    'ASSEMBLY', 
                    assembly['assemblyId'], 
                    'ASSEMBLY_COMP', 
                    component['componentId']
                )
            
            # Register material-component relationship
            if component.get('materialId') and component.get('componentId'):
                generator.id_registry.register_relationship(
                    'MATERIAL', 
                    component['materialId'], 
                    'ASSEMBLY_COMP', 
                    component['componentId']
                )
        
        # Generate case ID and link to scenario and assembly
        case_id = generator.id_registry.generate_id('CASE')
        generator.id_registry.register_entity('CASE', case_id, {'name': assembly.get('assemblyName', 'Case')})
        
        # Link to scenario if we have one
        scenario_ids = generator.id_registry.id_map.get('SCENARIO', [])
        if scenario_ids:
            generator.id_registry.register_relationship(
                'SCENARIO',
                scenario_ids[0],
                'CASE',
                case_id
            )
        
        # Link to assembly
        generator.id_registry.register_relationship(
            'ASSEMBLY',
            assembly['assemblyId'],
            'CASE',
            case_id
        )

def get_parent_id(generator, parent_type, child_type, child_id):
    """
    Find parent ID based on relationship.
    
    Args:
        generator: The XMLGenerator instance
        parent_type (str): Type of parent entity
        child_type (str): Type of child entity
        child_id (str): ID of child entity
        
    Returns:
        str: Parent ID or None
    """
    for (p_type, p_id, c_type), child_ids in generator.id_registry.relationship_map.items():
        if p_type == parent_type and c_type == child_type and child_id in child_ids:
            return p_id
    return None