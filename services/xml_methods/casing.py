# services/xml_methods/casing.py
from lxml import etree as ET
from utils.xml_helpers import convert_camel_to_xml_key, set_attributes_ordered
from services.xml_methods.utils import add_creation_info

def update_casing_schematics(generator, export_elem, casing_schematics):
    """
    Update casing schematics in the XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
        casing_schematics (dict): Casing schematics
    """
    if not casing_schematics:
        return
    
    # Get IDs
    well_ids = generator.id_registry.id_map.get('WELL', [])
    wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
    
    # Update materials
    if 'materials' in casing_schematics:
        for material in casing_schematics['materials']:
            # Prepare attributes
            attributes = {}
            
            # Set ID
            if 'materialId' in material:
                attributes["MATERIAL_ID"] = material['materialId']
            
            # Set required attributes for material
            if 'grade' in material:
                attributes["GRADE"] = str(material['grade'])
            if 'thermalExpansionCoef' in material:
                attributes["THERMAL_EXPANSION_COEF"] = str(material['thermalExpansionCoef'])
            if 'poissonsRatio' in material:
                attributes["POISSONS_RATIO"] = str(material['poissonsRatio'])
            if 'ultimateTensileStrength' in material:
                attributes["ULTIMATE_TENSILE_STRENGTH"] = str(material['ultimateTensileStrength'])
            if 'minYieldStress' in material:
                attributes["MIN_YIELD_STRESS"] = str(material['minYieldStress'])
            
            # Material name is required
            if 'materialName' in material:
                attributes["MATERIAL_NAME"] = material['materialName']
            
            # Set other attributes
            for key, value in material.items():
                if key not in ['materialId', 'grade', 'thermalExpansionCoef', 'poissonsRatio', 
                              'ultimateTensileStrength', 'minYieldStress', 'materialName']:
                    xml_key = convert_camel_to_xml_key(key)
                    attributes[xml_key] = str(value)
            
            # Create material element
            mat_elem = ET.SubElement(export_elem, "CD_MATERIAL")
            set_attributes_ordered(mat_elem, attributes)
            
            # Add creation info
            add_creation_info(generator, mat_elem)
    
    # Update assemblies
    if 'assemblies' in casing_schematics:
        for assembly in casing_schematics['assemblies']:
            # Prepare attributes
            attributes = {}
            
            # Set IDs
            if 'assemblyId' in assembly:
                attributes["ASSEMBLY_ID"] = assembly['assemblyId']
            
            # Set wellbore ID and well ID
            if wellbore_ids:
                attributes["WELLBORE_ID"] = wellbore_ids[0]
                # Set well ID if available
                if well_ids:
                    attributes["WELL_ID"] = well_ids[0]
            
            # Set required attributes for assembly
            if 'topDepth' in assembly:
                attributes["TOP_DEPTH"] = str(assembly['topDepth'])
                attributes["MD_ASSEMBLY_TOP"] = str(assembly['topDepth'])
                attributes["MD_TOC"] = str(assembly['topDepth'])
            
            if 'baseDepth' in assembly:
                attributes["BASE_DEPTH"] = str(assembly['baseDepth'])
                attributes["MD_ASSEMBLY_BASE"] = str(assembly['baseDepth'])
            
            # Set other attributes
            for key, value in assembly.items():
                if key not in ['assemblyId', 'wellboreId', 'components', 'topDepth', 'baseDepth']:
                    xml_key = convert_camel_to_xml_key(key)
                    attributes[xml_key] = str(value)
            
            # Add standard flags
            attributes["IS_TOP_DOWN"] = "Y"
            
            # Create assembly element
            assembly_elem = ET.SubElement(export_elem, "CD_ASSEMBLY")
            set_attributes_ordered(assembly_elem, attributes)
            
            # Add creation info
            add_creation_info(generator, assembly_elem)
            
            # Update components
            if 'components' in assembly:
                for i, component in enumerate(assembly['components']):
                    # Prepare attributes
                    comp_attributes = {}
                    
                    # Set IDs
                    if 'componentId' in component:
                        comp_attributes["ASSEMBLY_COMP_ID"] = component['componentId']
                    
                    # Set assembly ID
                    if 'assemblyId' in assembly:
                        comp_attributes["ASSEMBLY_ID"] = assembly['assemblyId']
                    
                    # Set wellbore and well IDs
                    if wellbore_ids:
                        comp_attributes["WELLBORE_ID"] = wellbore_ids[0]
                        if well_ids:
                            comp_attributes["WELL_ID"] = well_ids[0]
                    
                    # Set component type
                    comp_type = component.get('componentType', '').upper()
                    if comp_type == 'CASING':
                        comp_attributes["SECT_TYPE_CODE"] = "CAS"
                        comp_attributes["COMP_TYPE_CODE"] = "CAS"
                    elif comp_type == 'TUBING':
                        comp_attributes["SECT_TYPE_CODE"] = "TUB"
                        comp_attributes["COMP_TYPE_CODE"] = "TUB"
                    elif comp_type == 'LINER':
                        comp_attributes["SECT_TYPE_CODE"] = "LIN"
                        comp_attributes["COMP_TYPE_CODE"] = "LIN"
                    
                    # Set material ID if provided
                    if 'materialId' in component:
                        comp_attributes["MATERIAL_ID"] = component['materialId']
                    
                    # Set other attributes with appropriate naming conversion
                    for key, value in component.items():
                        if key not in ['componentId', 'assemblyId', 'wellboreId', 'componentType', 'materialId']:
                            # Handle special naming cases
                            if key == 'outerDiameter':
                                comp_attributes["OD_BODY"] = str(value)
                            elif key == 'innerDiameter':
                                comp_attributes["ID_BODY"] = str(value)
                            elif key == 'topDepth':
                                comp_attributes["MD_TOP"] = str(value)
                            elif key == 'bottomDepth':
                                comp_attributes["MD_BASE"] = str(value)
                            elif key == 'axialStrength':
                                comp_attributes["AXIAL_RATING"] = str(value)
                            elif key == 'weight':
                                comp_attributes["APPROXIMATE_WEIGHT"] = str(value)
                            else:
                                xml_key = convert_camel_to_xml_key(key)
                                comp_attributes[xml_key] = str(value)
                    
                    # Set sequence number
                    comp_attributes["SEQUENCE_NO"] = str(float(i))
                    
                    # Create component element
                    comp_elem = ET.SubElement(export_elem, "CD_ASSEMBLY_COMP")
                    set_attributes_ordered(comp_elem, comp_attributes)
                    
                    # Add creation info
                    add_creation_info(generator, comp_elem)