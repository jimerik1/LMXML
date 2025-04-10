# services/xml_methods/clear.py

def clear_template_elements(generator, export_elem, payload):
    """
    Clear elements from the template that will be replaced by payload data.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        payload (dict): Structured data payload
    """
    # Only clear elements if corresponding payload data exists
    if 'projectInfo' in payload:
        project_info = payload['projectInfo']
        
        # Clear site info if present in payload
        if 'site' in project_info:
            for site in export_elem.findall("./CD_SITE"):
                export_elem.remove(site)
        
        # Clear well info if present in payload
        if 'well' in project_info:
            for well in export_elem.findall("./CD_WELL"):
                export_elem.remove(well)
        
        # Clear wellbore info if present in payload
        if 'wellbore' in project_info:
            for wellbore in export_elem.findall("./CD_WELLBORE"):
                export_elem.remove(wellbore)
    
    # Clear formation inputs if present in payload
    if 'formationInputs' in payload:
        formation_inputs = payload['formationInputs']
        
        # Clear temperature profiles if present
        if 'temperatureProfiles' in formation_inputs:
            for temp in export_elem.findall("./CD_TEMPERATURE"):
                export_elem.remove(temp)
            for temp in export_elem.findall("./CD_TEMP_GRADIENT"):
                export_elem.remove(temp)
            for temp in export_elem.findall("./CD_TEMP_GRADIENT_GROUP"):
                export_elem.remove(temp)
        
        # Clear pressure profiles if present
        if 'pressureProfiles' in formation_inputs:
            for pressure in export_elem.findall("./CD_PORE_PRESSURE"):
                export_elem.remove(pressure)
            for pressure in export_elem.findall("./CD_FRAC_PRESSURE"):
                export_elem.remove(pressure)
            for pressure in export_elem.findall("./CD_HYDROSTATIC_PRESSURE"):
                export_elem.remove(pressure)
            for pressure in export_elem.findall("./CD_PORE_PRESSURE_GROUP"):
                export_elem.remove(pressure)
            for pressure in export_elem.findall("./CD_FRAC_GRADIENT_GROUP"):
                export_elem.remove(pressure)
            for pressure in export_elem.findall("./CD_FRAC_GRADIENT"):
                export_elem.remove(pressure)
        
        # Clear DLS overrides if present
        if 'dlsOverrideGroup' in formation_inputs:
            for dls_group in export_elem.findall("./TU_DLS_OVERRIDE_GROUP"):
                export_elem.remove(dls_group)
            for dls_override in export_elem.findall("./TU_DLS_OVERRIDE"):
                export_elem.remove(dls_override)
        
        # Clear survey data if present
        if 'surveyHeader' in formation_inputs:
            for header in export_elem.findall("./CD_DEFINITIVE_SURVEY_HEADER"):
                export_elem.remove(header)
            for station in export_elem.findall("./CD_DEFINITIVE_SURVEY_STATION"):
                export_elem.remove(station)
    
    # Clear casing schematics if present in payload
    if 'casingSchematics' in payload:
        casing_schematics = payload['casingSchematics']
        
        # Clear materials if present
        if 'materials' in casing_schematics:
            for material in export_elem.findall("./CD_MATERIAL"):
                export_elem.remove(material)
        
        # Clear assemblies if present
        if 'assemblies' in casing_schematics:
            for assembly in export_elem.findall("./CD_ASSEMBLY"):
                export_elem.remove(assembly)
            
            # Also clear assembly components
            for component in export_elem.findall("./CD_ASSEMBLY_COMP"):
                export_elem.remove(component)
    
    # Clear datum if present
    if 'datum' in payload:
        for datum in export_elem.findall("./CD_DATUM"):
            export_elem.remove(datum)
    
    # Always clear existing cases and scenarios - this prevents duplicates
    for case in export_elem.findall("./CD_CASE"):
        export_elem.remove(case)
    
    for scenario in export_elem.findall("./CD_SCENARIO"):
        export_elem.remove(scenario)
    
    # Clear any packer elements
    for packer in export_elem.findall("./CD_WEQP_PACKER"):
        export_elem.remove(packer)
        
    # Always clear any existing BINARY_DATA elements
    for binary_data in export_elem.findall("./BINARY_DATA"):
        export_elem.remove(binary_data)