# services/xml/casing_handlers.py
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from lxml import etree as ET

from services.xml.utils import generate_random_id
from services.xml.element_operations import create_element, remove_existing_elements

logger = logging.getLogger(__name__)

def update_casing_assemblies(root: ET.Element, well_id: str, wellbore_id: str,
                           assemblies: List[Dict[str, Any]]) -> bool:
    """
    Update casing assemblies and their components in the XML.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        assemblies: List of assembly data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Updating {len(assemblies)} casing assemblies")
        
        # Get existing assembly IDs to reuse
        existing_assemblies = root.xpath(".//CD_ASSEMBLY")
        existing_ids = [elem.get('ASSEMBLY_ID') for elem in existing_assemblies]
        
        # Keep track of created assemblies for updating CASE elements later
        created_assemblies = []
        
        # Process each assembly
        for i, assembly in enumerate(assemblies):
            # Reuse IDs for first 5 assemblies if available, otherwise generate new ones
            assembly_id = assembly.get('assemblyId')
            if not assembly_id:
                if i < len(existing_ids):
                    assembly_id = existing_ids[i]
                else:
                    assembly_id = generate_random_id()
            
            # Remove existing assembly with this ID if it exists
            remove_existing_elements(root, f".//CD_ASSEMBLY[@ASSEMBLY_ID='{assembly_id}']")
            
            # Create new assembly
            assembly_attrs = {
                'WELL_ID': well_id,
                'WELLBORE_ID': wellbore_id,
                'ASSEMBLY_ID': assembly_id,
                'STRING_TYPE': assembly.get('stringType'),
                'STRING_CLASS': assembly.get('stringClass', ''),
                'ASSEMBLY_NAME': assembly.get('assemblyName'),
                'ASSEMBLY_SIZE': str(assembly.get('assemblySize', 0)),
                'HOLE_SIZE': str(assembly.get('holeSize', 0)),
                'MD_ASSEMBLY_BASE': str(assembly.get('baseDepth')),
                'MD_ASSEMBLY_TOP': str(assembly.get('topDepth')),
                'MD_TOC': str(assembly.get('tocDepth', assembly.get('topDepth'))),
                'MUD_DENSITY_SHOE': str(assembly.get('mudDensityShoe', 0)),
                'IS_TOP_DOWN': assembly.get('isTopDown', 'Y'),
                'CREATE_DATE': f"{{ts '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'}}",
                'CREATE_USER_ID': 'API_USER',
                'CREATE_APP_ID': 'XML_API',
                'UPDATE_DATE': f"{{ts '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'}}",
                'UPDATE_USER_ID': 'API_USER',
                'UPDATE_APP_ID': 'XML_API'
            }
            
            # Create and add the element to the root
            assembly_elem = create_element('CD_ASSEMBLY', assembly_attrs)
            root.append(assembly_elem)
            
            logger.info(f"Added assembly: {assembly.get('assemblyName')}, ID: {assembly_id}")
            created_assemblies.append({
                'id': assembly_id,
                'name': assembly.get('assemblyName')
            })
            
            # Process components for this assembly
            if 'components' in assembly and assembly['components']:
                update_assembly_components(root, well_id, wellbore_id, assembly_id, assembly['components'])
            
        # Update CASE elements to reflect the assemblies
        update_case_elements(root, well_id, wellbore_id, created_assemblies)
            
        return True
    except Exception as e:
        logger.error(f"Error updating casing assemblies: {str(e)}", exc_info=True)
        return False

def update_assembly_components(root: ET.Element, well_id: str, wellbore_id: str, 
                             assembly_id: str, components: List[Dict[str, Any]]) -> bool:
    """
    Update assembly components in the XML.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        assembly_id: Assembly ID
        components: List of component data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Updating {len(components)} components for assembly {assembly_id}")
        
        # Remove existing components for this assembly
        remove_existing_elements(root, f".//CD_ASSEMBLY_COMP[@ASSEMBLY_ID='{assembly_id}']")
        remove_existing_elements(root, f".//CD_WEQP_PACKER[@ASSEMBLY_ID='{assembly_id}']")
        
        # Process each component
        for i, component in enumerate(components):
            # Generate a new ID for the component
            component_id = component.get('componentId', generate_random_id())
            
            # Basic attributes for all component types
            component_attrs = {
                'WELL_ID': well_id,
                'WELLBORE_ID': wellbore_id,
                'ASSEMBLY_ID': assembly_id,
                'ASSEMBLY_COMP_ID': component_id,
                'COMP_TYPE_CODE': component.get('componentType'),
                'SECT_TYPE_CODE': component.get('componentType'),
                'SEQUENCE_NO': str(float(i)),
                'CREATE_DATE': f"{{ts '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'}}",
                'CREATE_USER_ID': 'API_USER',
                'CREATE_APP_ID': 'XML_API',
                'UPDATE_DATE': f"{{ts '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'}}",
                'UPDATE_USER_ID': 'API_USER',
                'UPDATE_APP_ID': 'XML_API'
            }
            
            # Add physical properties for non-PKR types
            if component.get('componentType') != 'PKR':
                component_attrs.update({
                    'OD_BODY': str(component.get('outerDiameter')),
                    'ID_BODY': str(component.get('innerDiameter')),
                    'LENGTH': str(component.get('length')),
                    'MD_TOP': str(component.get('topDepth')),
                    'MD_BASE': str(component.get('bottomDepth')),
                    'CONNECTION_TYPE': str(component.get('connectionType', '')),
                    'GRADE': component.get('grade', ''),
                    'APPROXIMATE_WEIGHT': str(component.get('weight', 0)),
                    'PRESSURE_BURST': str(component.get('pressureBurst', 0)),
                    'PRESSURE_COLLAPSE': str(component.get('pressureCollapse', 0)),
                    'AXIAL_RATING': str(component.get('axialStrength', 0))
                })
                
                # Add optional properties if provided
                if 'jointStrength' in component:
                    component_attrs['JOINT_STRENGTH'] = str(component.get('jointStrength', 0))
                if 'pipeType' in component:
                    component_attrs['PIPE_TYPE'] = component.get('pipeType', 'Standard')
                if 'poissonsRatio' in component:
                    component_attrs['POISSONS_RATIO'] = str(component.get('poissonsRatio', 0))
                if 'minYieldStress' in component:
                    component_attrs['MIN_YIELD_STRESS'] = str(component.get('minYieldStress', 0))
                if 'ultimateTensileStrength' in component:
                    component_attrs['ULTIMATE_TENSILE_STRENGTH'] = str(component.get('ultimateTensileStrength', 0))
                if 'thermalExpansionCoef' in component:
                    component_attrs['THERMAL_EXPANSION_COEF'] = str(component.get('thermalExpansionCoef', 0))
                if 'youngsModulus' in component:
                    component_attrs['YOUNGS_MODULUS'] = str(component.get('youngsModulus', 0))
                if 'wallThicknessPercent' in component:
                    component_attrs['WALL_THICKNESS_PERCENT'] = str(component.get('wallThicknessPercent', 0))
                
                # Add connection properties if present
                if 'connectionName' in component:
                    component_attrs['CONNECTION_NAME'] = component.get('connectionName', '')
                if 'connectionGrade' in component:
                    component_attrs['CONNECTION_GRADE'] = component.get('connectionGrade', '')
                
                # Add material reference if provided
                if 'materialId' in component and component['materialId']:
                    component_attrs['MATERIAL_ID'] = component['materialId']
            
            # Create the element
            component_elem = create_element('CD_ASSEMBLY_COMP', component_attrs)
            
            # Add to the root
            root.append(component_elem)
            
            logger.info(f"Added component: {component.get('componentType')}, ID: {component_id}")
            
            # Add additional elements for special component types (like packers)
            if component.get('componentType') == 'PKR':
                add_packer_details(root, well_id, wellbore_id, assembly_id, component_id, component)
        
        return True
    except Exception as e:
        logger.error(f"Error updating assembly components: {str(e)}", exc_info=True)
        return False

def add_packer_details(root: ET.Element, well_id: str, wellbore_id: str, 
                     assembly_id: str, component_id: str, component: Dict[str, Any]) -> None:
    """
    Add packer-specific details for packer components.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        assembly_id: Assembly ID
        component_id: Component ID
        component: Component data
    """
    try:
        # Create packer-specific attributes
        packer_attrs = {
            'WELL_ID': well_id,
            'WELLBORE_ID': wellbore_id,
            'ASSEMBLY_ID': assembly_id,
            'ASSEMBLY_COMP_ID': component_id,
            'PACKER_NAME': component.get('packerName', 'TOC'),
            'PACKER_DEPTH': str(component.get('packerDepth', component.get('topDepth', 0))),
            'PLUG_DEPTH': str(component.get('plugDepth', component.get('bottomDepth', 0))),
            'BORE_INNER_DIAMETER': str(component.get('innerDiameter', 0)),
            'HYDRAULIC_SET_PRESSURE': '0.0',
            'SLIP_TYPE': '0',
            'AXIAL_LOAD_CHANGE': '0.0',
            'AXIAL_LOAD_CHANGE_DIRECTION': '0',
            'IS_SEAL_BORE_PRESENT': 'N',
            'SEAL_ASSEMBLY_TYPE': '0',
            'IS_SEAL_MOVEMENT_ALLOWED': 'N',
            'UPWARD_MOVEMENT_LEN': '30.0',
            'DOWNWARD_MOVEMENT_LEN': '0.0',
            'IS_UPWARD_NOGO_PRESENT': 'N',
            'IS_DOWNWARD_NOGO_PRESENT': 'N',
            'UPWARD_MOVEMENT_LENGTH': '0.0',
            'DOWNWARD_MOVEMENT_LENGTH': '0.0',
            'PACKER_TYPE_FLAG': '8.0',
            'RUNNING_STRING_FLAG': '0.0',
            'SET_TYPE': '0.0',
            'HYDROSTATIC_SET_PRESSURE': '0.0',
            'IS_ANNULAR_VALVE_SEAL_OPEN': 'N',
            'EXPANSION_JOINT_DEPTH': str(float(component.get('packerDepth', 0)) - 1.0),
            'IS_SHEARED': 'N',
            'SHEAR_PIN_RATING': '10000.0',
            'PBR_TOTAL_STROKE': '30.0',
            'IS_SPACED_OUT': 'N',
            'IS_EXP_JOINT_NOGO_PRESENT': 'N'
        }
        
        # Create the element
        packer_elem = create_element('CD_WEQP_PACKER', packer_attrs)
        
        # Add to the root
        root.append(packer_elem)
        
        logger.info(f"Added packer details for component ID: {component_id}")
    except Exception as e:
        logger.error(f"Error adding packer details: {str(e)}", exc_info=True)

def update_case_elements(root: ET.Element, well_id: str, wellbore_id: str, 
                       assemblies: List[Dict[str, Any]]) -> bool:
    """
    Update CASE elements to reflect the assemblies.
    
    Args:
        root: Root XML element
        well_id: Well ID
        wellbore_id: Wellbore ID
        assemblies: List of created assembly info
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Updating CASE elements for assemblies")
        
        # Find scenario ID
        scenario_elements = root.xpath(".//CD_SCENARIO")
        if not scenario_elements:
            logger.warning("No CD_SCENARIO element found")
            return False
        
        scenario_id = scenario_elements[0].get('SCENARIO_ID')
        
        # Remove existing CASE elements
        for assembly in assemblies:
            remove_existing_elements(root, f".//CD_CASE[@ASSEMBLY_ID='{assembly['id']}']")
        
        # Create a CASE element for each assembly
        for i, assembly in enumerate(assemblies):
            case_id = generate_random_id()
            
            case_attrs = {
                'WELL_ID': well_id,
                'WELLBORE_ID': wellbore_id,
                'SCENARIO_ID': scenario_id,
                'CASE_ID': case_id,
                'CASE_NAME': assembly['name'],
                'ASSEMBLY_ID': assembly['id'],
                'IS_LINKED': 'Y',
                'SEQUENCE_NO': str(float(i)),
                'CREATE_DATE': f"{{ts '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'}}",
                'CREATE_USER_ID': 'API_USER',
                'CREATE_APP_ID': 'XML_API',
                'UPDATE_DATE': f"{{ts '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'}}",
                'UPDATE_USER_ID': 'API_USER',
                'UPDATE_APP_ID': 'XML_API'
            }
            
            # Create and add the element
            case_elem = create_element('CD_CASE', case_attrs)
            root.append(case_elem)
            
            logger.info(f"Added CASE element for assembly: {assembly['name']}, ID: {assembly['id']}")
        
        return True
    except Exception as e:
        logger.error(f"Error updating CASE elements: {str(e)}", exc_info=True)
        return False