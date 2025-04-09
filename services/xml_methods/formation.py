# services/xml_methods/formation.py
from lxml import etree as ET
from services.xml_methods.utils import add_creation_info

def update_formation_inputs(generator, export_elem, formation_inputs):
    """
    Update formation inputs in the XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        formation_inputs (dict): Formation inputs
    """
    if not formation_inputs:
        return
    
    # Get IDs
    well_ids = generator.id_registry.id_map.get('WELL', [])
    wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
    
    # Update temperature profiles
    if 'temperatureProfiles' in formation_inputs:
        # Create temperature gradient group
        temp_group_elem = ET.SubElement(export_elem, "CD_TEMP_GRADIENT_GROUP")
        temp_group_ids = generator.id_registry.id_map.get('TEMP_GRADIENT_GROUP', [])
        temp_group_id = temp_group_ids[0] if temp_group_ids else generator.id_registry.generate_id('TEMP_GRADIENT_GROUP')
        temp_group_elem.set("TEMP_GRADIENT_GROUP_ID", temp_group_id)
        temp_group_elem.set("NAME", "Geothermal Gradient")
        temp_group_elem.set("PHASE", "PROTOTYPE")
        
        # Add wellbore and well IDs
        if wellbore_ids:
            temp_group_elem.set("WELLBORE_ID", wellbore_ids[0])
            if well_ids:
                temp_group_elem.set("WELL_ID", well_ids[0])
        
        # Add surface ambient temp if first profile is at depth 0
        surface_temp = None
        for profile in formation_inputs['temperatureProfiles']:
            if profile['depth'] == 0:
                surface_temp = profile['temperature']
                temp_group_elem.set("SURFACE_AMBIENT_TEMP", str(surface_temp))
                break
        
        # Add creation info
        add_creation_info(generator, temp_group_elem)
        
        # Add temperature profile points
        for profile in formation_inputs['temperatureProfiles']:
            if profile['depth'] > 0:  # Skip surface temp which is already in the group
                temp_elem = ET.SubElement(export_elem, "CD_TEMP_GRADIENT")
                temp_elem.set("TEMP_GRADIENT_GROUP_ID", temp_group_id)
                temp_elem.set("TEMP_GRADIENT_ID", generator.id_registry.generate_id('TEMP_GRADIENT'))
                temp_elem.set("TEMPERATURE", str(profile['temperature']))
                temp_elem.set("TVD", str(profile['depth']))
                
                # Add wellbore and well IDs
                if wellbore_ids:
                    temp_elem.set("WELLBORE_ID", wellbore_ids[0])
                    if well_ids:
                        temp_elem.set("WELL_ID", well_ids[0])
    
    # Update pressure profiles
    if 'pressureProfiles' in formation_inputs:
        # Group pressure profiles by type
        pore_pressures = []
        frac_pressures = []
        hydrostatic_pressures = []
        
        for profile in formation_inputs['pressureProfiles']:
            if profile['pressureType'] == 'Pore':
                pore_pressures.append(profile)
            elif profile['pressureType'] == 'Frac':
                frac_pressures.append(profile)
            elif profile['pressureType'] == 'Hydrostatic':
                hydrostatic_pressures.append(profile)
        
        # Create pore pressure group if needed
        if pore_pressures:
            pore_group_elem = ET.SubElement(export_elem, "CD_PORE_PRESSURE_GROUP")
            pore_group_ids = generator.id_registry.id_map.get('PORE_PRESSURE_GROUP', [])
            pore_group_id = pore_group_ids[0] if pore_group_ids else generator.id_registry.generate_id('PORE_PRESSURE_GROUP')
            pore_group_elem.set("PORE_PRESSURE_GROUP_ID", pore_group_id)
            pore_group_elem.set("NAME", "Pore Pressure")
            pore_group_elem.set("PHASE", "PROTOTYPE")
            
            # Add wellbore and well IDs
            if wellbore_ids:
                pore_group_elem.set("WELLBORE_ID", wellbore_ids[0])
                if well_ids:
                    pore_group_elem.set("WELL_ID", well_ids[0])
            
            # Add creation info
            add_creation_info(generator, pore_group_elem)
            
            # Add pore pressure points
            for pressure in pore_pressures:
                press_elem = ET.SubElement(export_elem, "CD_PORE_PRESSURE")
                press_elem.set("PORE_PRESSURE_GROUP_ID", pore_group_id)
                press_elem.set("PORE_PRESSURE_ID", generator.id_registry.generate_id('PORE_PRESSURE'))
                press_elem.set("PORE_PRESSURE", str(pressure['pressure']))
                press_elem.set("TVD", str(pressure['depth']))
                press_elem.set("IS_PERMEABLE_ZONE", "Y")
                
                # Calculate EMW if not provided
                if 'emw' in pressure:
                    press_elem.set("PORE_PRESSURE_EMW", str(pressure['emw']))
                else:
                    # Simple EMW calculation (pressure / (0.052 * depth))
                    emw = pressure['pressure'] / (0.052 * pressure['depth']) if pressure['depth'] > 0 else 0
                    press_elem.set("PORE_PRESSURE_EMW", str(emw))
                
                # Add wellbore and well IDs
                if wellbore_ids:
                    press_elem.set("WELLBORE_ID", wellbore_ids[0])
                    if well_ids:
                        press_elem.set("WELL_ID", well_ids[0])
        
        # Create frac gradient group if needed
        if frac_pressures:
            frac_group_elem = ET.SubElement(export_elem, "CD_FRAC_GRADIENT_GROUP")
            frac_group_ids = generator.id_registry.id_map.get('FRAC_GRADIENT_GROUP', [])
            frac_group_id = frac_group_ids[0] if frac_group_ids else generator.id_registry.generate_id('FRAC_GRADIENT_GROUP')
            frac_group_elem.set("FRAC_GRADIENT_GROUP_ID", frac_group_id)
            frac_group_elem.set("NAME", "Frac Gradient")
            frac_group_elem.set("PHASE", "PROTOTYPE")
            
            # Add wellbore and well IDs
            if wellbore_ids:
                frac_group_elem.set("WELLBORE_ID", wellbore_ids[0])
                if well_ids:
                    frac_group_elem.set("WELL_ID", well_ids[0])
            
            # Add creation info
            add_creation_info(generator, frac_group_elem)
            
            # Add frac pressure points
            for pressure in frac_pressures:
                frac_elem = ET.SubElement(export_elem, "CD_FRAC_GRADIENT")
                frac_elem.set("FRAC_GRADIENT_GROUP_ID", frac_group_id)
                frac_elem.set("FRAC_GRADIENT_ID", generator.id_registry.generate_id('FRAC_GRADIENT'))
                frac_elem.set("FRAC_GRADIENT_PRESSURE", str(pressure['pressure']))
                frac_elem.set("TVD", str(pressure['depth']))
                
                # Calculate EMW if not provided
                if 'emw' in pressure:
                    frac_elem.set("FRAC_GRADIENT_EMW", str(pressure['emw']))
                else:
                    # Simple EMW calculation (pressure / (0.052 * depth))
                    emw = pressure['pressure'] / (0.052 * pressure['depth']) if pressure['depth'] > 0 else 0
                    frac_elem.set("FRAC_GRADIENT_EMW", str(emw))
                
                # Add wellbore and well IDs
                if wellbore_ids:
                    frac_elem.set("WELLBORE_ID", wellbore_ids[0])
                    if well_ids:
                        frac_elem.set("WELL_ID", well_ids[0])