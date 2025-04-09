# services/xml_methods/casing.py
from lxml import etree as ET
from utils.xml_helpers import convert_camel_to_xml_key
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
            mat_elem = ET.SubElement(export_elem, "CD_MATERIAL")
            
            # Set ID
            if 'materialId' in material:
                mat_elem.set("MATERIAL_ID", material['materialId'])
            
            # Set required attributes for material
            if 'grade' in material:
                mat_elem.set("GRADE", str(material['grade']))
            if 'thermalExpansionCoef' in material:
                mat_elem.set("THERMAL_EXPANSION_COEF", str(material['thermalExpansionCoef']))
            if 'poissonsRatio' in material:
                mat_elem.set("POISSONS_RATIO", str(material['poissonsRatio']))
            if 'ultimateTensileStrength' in material:
                mat_elem.set("ULTIMATE_TENSILE_STRENGTH", str(material['ultimateTensileStrength']))
            if 'minYieldStress' in material:
                mat_elem.set("MIN_YIELD_STRESS", str(material['minYieldStress']))
            
            # Material name is required
            if 'materialName' in material:
                mat_elem.set("MATERIAL_NAME", material['materialName'])
            
            # Set other attributes
            for key, value in material.items():
                if key not in ['materialId', 'grade', 'thermalExpansionCoef', 'poissonsRatio', 
                              'ultimateTensileStrength', 'minYieldStress', 'materialName']:
                    xml_key = convert_camel_to_xml_key(key)
                    mat_elem.set(xml_key, str(value))
            
            # Add creation info
            add_creation_info(generator, mat_elem)
    
    # Update assemblies
    if 'assemblies' in casing_schematics:
        for assembly in casing_schematics['assemblies']:
            # Create assembly element
            assembly_elem = ET.SubElement(export_elem, "CD_ASSEMBLY")
            
            # Set IDs
            if 'assemblyId' in assembly:
                assembly_elem.set("ASSEMBLY_ID", assembly['assemblyId'])
            
            # Set wellbore ID
            if wellbore_ids:
                assembly_elem.set("WELLBORE_ID", wellbore_ids[0])
                # Set well ID if available
                if well_ids:
                    assembly_elem.set("WELL_ID", well_ids[0])
            
            # Set required attributes for assembly
            if 'topDepth' in assembly:
                assembly_elem.set("TOP_DEPTH", str(assembly['topDepth']))
                assembly_elem.set("MD_ASSEMBLY_TOP", str(assembly['topDepth']))
                assembly_elem.set("MD_TOC", str(assembly['topDepth']))
            
            if 'baseDepth' in assembly:
                assembly_elem.set("BASE_DEPTH", str(assembly['baseDepth']))
                assembly_elem.set("MD_ASSEMBLY_BASE", str(assembly['baseDepth']))
            
            # Set other attributes
            for key, value in assembly.items():
                if key not in ['assemblyId', 'wellboreId', 'components', 'topDepth', 'baseDepth']:
                    xml_key = convert_camel_to_xml_key(key)
                    assembly_elem.set(xml_key, str(value))
            
            # Add creation info and standard flags
            add_creation_info(generator, assembly_elem)
            assembly_elem.set("IS_TOP_DOWN", "Y")
            
            # Update components
            if 'components' in assembly:
                for i, component in enumerate(assembly['components']):
                    # Create component element
                    comp_elem = ET.SubElement(export_elem, "CD_ASSEMBLY_COMP")
                    
                    # Set IDs
                    if 'componentId' in component:
                        comp_elem.set("ASSEMBLY_COMP_ID", component['componentId'])
                    
                    # Set assembly ID
                    if 'assemblyId' in assembly:
                        comp_elem.set("ASSEMBLY_ID", assembly['assemblyId'])
                    
                    # Set wellbore and well IDs
                    if wellbore_ids:
                        comp_elem.set("WELLBORE_ID", wellbore_ids[0])
                        if well_ids:
                            comp_elem.set("WELL_ID", well_ids[0])
                    
                    # Set component type
                    comp_type = component.get('componentType', '').upper()
                    if comp_type == 'CASING':
                        comp_elem.set("SECT_TYPE_CODE", "CAS")
                        comp_elem.set("COMP_TYPE_CODE", "CAS")
                    elif comp_type == 'TUBING':
                        comp_elem.set("SECT_TYPE_CODE", "TUB")
                        comp_elem.set("COMP_TYPE_CODE", "TUB")
                    elif comp_type == 'LINER':
                        comp_elem.set("SECT_TYPE_CODE", "LIN")
                        comp_elem.set("COMP_TYPE_CODE", "LIN")
                    
                    # Set material ID if provided
                    if 'materialId' in component:
                        comp_elem.set("MATERIAL_ID", component['materialId'])
                    
                    # Set other attributes with appropriate naming conversion
                    for key, value in component.items():
                        if key not in ['componentId', 'assemblyId', 'wellboreId', 'componentType', 'materialId']:
                            # Handle special naming cases
                            if key == 'outerDiameter':
                                comp_elem.set("OD_BODY", str(value))
                            elif key == 'innerDiameter':
                                comp_elem.set("ID_BODY", str(value))
                            elif key == 'topDepth':
                                comp_elem.set("MD_TOP", str(value))
                            elif key == 'bottomDepth':
                                comp_elem.set("MD_BASE", str(value))
                            elif key == 'axialStrength':
                                comp_elem.set("AXIAL_RATING", str(value))
                            elif key == 'weight':
                                comp_elem.set("APPROXIMATE_WEIGHT", str(value))
                            else:
                                xml_key = convert_camel_to_xml_key(key)
                                comp_elem.set(xml_key, str(value))
                    
                    # Set sequence number
                    comp_elem.set("SEQUENCE_NO", str(float(i)))
                    
                    # Add creation info
                    add_creation_info(generator, comp_elem)