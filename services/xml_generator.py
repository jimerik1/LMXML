# services/xml_generator.py
from lxml import etree as ET
from datetime import datetime
from services.id_registry import IDRegistry
from utils.xml_helpers import (
    load_xml_template, 
    convert_camel_to_xml_key,
    find_element_by_attributes,
    create_or_update_element,
    xml_to_string,
    format_timestamp
)

class XMLGenerator:
    """
    Service for generating XML files from structured data.
    
    This generator preserves the structure of a base template while
    updating specific elements based on the provided payload.
    """
    
    def __init__(self, base_template_path):
        """
        Initialize the XML generator with a template path.
        
        Args:
            base_template_path (str): Path to the base XML template
        """
        self.base_template_path = base_template_path
        self.id_registry = IDRegistry()
    
    def generate_xml(self, payload):
        """
        Generate XML from a structured payload by updating the template.
        
        Args:
            payload (dict): Structured data payload
            
        Returns:
            str: Generated XML as a string
        """
        # Load the template
        tree = load_xml_template(self.base_template_path)
        root = tree.getroot()
        
        # Find the export element
        export_elem = root.find(".//export")
        if export_elem is None:
            raise ValueError("Template XML does not contain an export element")
        
        # Generate and register IDs as needed
        self._prepare_ids(payload)
        
        # Clear existing elements that will be replaced
        self._clear_template_elements(export_elem, payload)
        
        # Update the XML structure
        self._update_project_info(export_elem, payload.get('projectInfo', {}))
        self._update_formation_inputs(export_elem, payload.get('formationInputs', {}))
        self._update_casing_schematics(export_elem, payload.get('casingSchematics', {}))
        
        # Validate relationships
        validation_errors = self.id_registry.validate_references()
        if validation_errors:
            raise ValueError("\n".join(validation_errors))
        
        # Return the XML as a string
        return xml_to_string(root)
    
    def _clear_template_elements(self, export_elem, payload):
        """
        Clear elements from the template that will be replaced by payload data.
        
        Args:
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
            
            # Clear pressure profiles if present
            if 'pressureProfiles' in formation_inputs:
                for pressure in export_elem.findall("./CD_PORE_PRESSURE"):
                    export_elem.remove(pressure)
                for pressure in export_elem.findall("./CD_FRAC_PRESSURE"):
                    export_elem.remove(pressure)
        
        # Clear casing schematics if present in payload
        if 'casingSchematics' in payload:
            casing_schematics = payload['casingSchematics']
            
            # Clear assemblies if present
            if 'assemblies' in casing_schematics:
                for assembly in export_elem.findall("./CD_ASSEMBLY"):
                    export_elem.remove(assembly)
                
                # Also clear assembly components
                for component in export_elem.findall("./CD_ASSEMBLY_COMP"):
                    export_elem.remove(component)
    
    def _prepare_ids(self, payload):
        """
        Generate and register IDs for entities in the payload.
        Same implementation as before...
        """
        # Project info IDs
        project_info = payload.get('projectInfo', {})
        
        # Site ID
        site = project_info.get('site', {})
        if site and not site.get('siteId'):
            site['siteId'] = self.id_registry.generate_id('SITE')
        elif site and site.get('siteId'):
            self.id_registry.register_entity('SITE', site['siteId'], site)
        
        # Well ID
        well = project_info.get('well', {})
        if well and not well.get('wellId'):
            well['wellId'] = self.id_registry.generate_id('WELL')
        elif well and well.get('wellId'):
            self.id_registry.register_entity('WELL', well['wellId'], well)
        
        # Register site-well relationship
        if site and well and site.get('siteId') and well.get('wellId'):
            self.id_registry.register_relationship('SITE', site['siteId'], 'WELL', well['wellId'])
        
        # Wellbore ID
        wellbore = project_info.get('wellbore', {})
        if wellbore and not wellbore.get('wellboreId'):
            wellbore['wellboreId'] = self.id_registry.generate_id('WELLBORE')
        elif wellbore and wellbore.get('wellboreId'):
            self.id_registry.register_entity('WELLBORE', wellbore['wellboreId'], wellbore)
        
        # Register well-wellbore relationship
        if well and wellbore and well.get('wellId') and wellbore.get('wellboreId'):
            self.id_registry.register_relationship('WELL', well['wellId'], 'WELLBORE', wellbore['wellboreId'])
        
        # Casing schematics IDs
        casing_schematics = payload.get('casingSchematics', {})
        
        # Material IDs
        materials = casing_schematics.get('materials', [])
        for material in materials:
            if not material.get('materialId'):
                material['materialId'] = self.id_registry.generate_id('MATERIAL')
            else:
                self.id_registry.register_entity('MATERIAL', material['materialId'], material)
        
        # Assembly IDs
        assemblies = casing_schematics.get('assemblies', [])
        for assembly in assemblies:
            if not assembly.get('assemblyId'):
                assembly['assemblyId'] = self.id_registry.generate_id('ASSEMBLY')
            else:
                self.id_registry.register_entity('ASSEMBLY', assembly['assemblyId'], assembly)
            
            # Register wellbore-assembly relationship
            if wellbore and assembly.get('wellboreId') and assembly.get('assemblyId'):
                self.id_registry.register_relationship(
                    'WELLBORE', 
                    assembly['wellboreId'], 
                    'ASSEMBLY', 
                    assembly['assemblyId']
                )
            
            # Component IDs
            components = assembly.get('components', [])
            for component in components:
                if not component.get('componentId'):
                    component['componentId'] = self.id_registry.generate_id('ASSEMBLY_COMP')
                else:
                    self.id_registry.register_entity('ASSEMBLY_COMP', component['componentId'], component)
                
                # Register assembly-component relationship
                if assembly.get('assemblyId') and component.get('componentId'):
                    self.id_registry.register_relationship(
                        'ASSEMBLY', 
                        assembly['assemblyId'], 
                        'ASSEMBLY_COMP', 
                        component['componentId']
                    )
                
                # Register material-component relationship
                if component.get('materialId') and component.get('componentId'):
                    self.id_registry.register_relationship(
                        'MATERIAL', 
                        component['materialId'], 
                        'ASSEMBLY_COMP', 
                        component['componentId']
                    )
    
    def _update_project_info(self, export_elem, project_info):
        """
        Update project information in the XML.
        
        Args:
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
            
            # Add creation and update info
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            site_elem.set("CREATE_DATE", format_timestamp(now_str))
            site_elem.set("UPDATE_DATE", format_timestamp(now_str))
            site_elem.set("CREATE_USER_ID", "API_USER")
            site_elem.set("UPDATE_USER_ID", "API_USER")
            site_elem.set("CREATE_APP_ID", "XML_API")
            site_elem.set("UPDATE_APP_ID", "XML_API")
        
        # Update well information
        if 'well' in project_info:
            well_elem = ET.SubElement(export_elem, "CD_WELL")
            
            # Set attributes
            for key, value in project_info['well'].items():
                if key == 'wellId':
                    well_elem.set("WELL_ID", value)
                elif key == 'siteId':
                    well_elem.set("SITE_ID", value)
                else:
                    xml_key = convert_camel_to_xml_key(key)
                    well_elem.set(xml_key, str(value))
            
            # Add creation and update info
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            well_elem.set("CREATE_DATE", format_timestamp(now_str))
            well_elem.set("UPDATE_DATE", format_timestamp(now_str))
            well_elem.set("CREATE_USER_ID", "API_USER")
            well_elem.set("UPDATE_USER_ID", "API_USER")
            well_elem.set("CREATE_APP_ID", "XML_API")
            well_elem.set("UPDATE_APP_ID", "XML_API")
        
        # Update wellbore information
        if 'wellbore' in project_info:
            wellbore_elem = ET.SubElement(export_elem, "CD_WELLBORE")
            
            # Set attributes
            for key, value in project_info['wellbore'].items():
                if key == 'wellboreId':
                    wellbore_elem.set("WELLBORE_ID", value)
                elif key == 'wellId':
                    wellbore_elem.set("WELL_ID", value)
                else:
                    xml_key = convert_camel_to_xml_key(key)
                    wellbore_elem.set(xml_key, str(value))
            
            # Add creation and update info
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            wellbore_elem.set("CREATE_DATE", format_timestamp(now_str))
            wellbore_elem.set("UPDATE_DATE", format_timestamp(now_str))
            wellbore_elem.set("CREATE_USER_ID", "API_USER")
            wellbore_elem.set("UPDATE_USER_ID", "API_USER")
            wellbore_elem.set("CREATE_APP_ID", "XML_API")
            wellbore_elem.set("UPDATE_APP_ID", "XML_API")
    
    def _update_formation_inputs(self, export_elem, formation_inputs):
        """
        Update formation inputs in the XML.
        
        Args:
            export_elem (Element): Export XML element
            formation_inputs (dict): Formation inputs
        """
        if not formation_inputs:
            return
        
        # Update temperature profiles
        if 'temperatureProfiles' in formation_inputs:
            for profile in formation_inputs['temperatureProfiles']:
                temp_elem = ET.SubElement(export_elem, "CD_TEMPERATURE")
                
                # Set attributes
                temp_elem.set("DEPTH", str(profile['depth']))
                temp_elem.set("TEMPERATURE", str(profile['temperature']))
                if 'units' in profile:
                    temp_elem.set("UNITS", profile['units'])
                
                # Add creation and update info
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                temp_elem.set("CREATE_DATE", format_timestamp(now_str))
                temp_elem.set("UPDATE_DATE", format_timestamp(now_str))
                temp_elem.set("CREATE_USER_ID", "API_USER")
                temp_elem.set("UPDATE_USER_ID", "API_USER")
                temp_elem.set("CREATE_APP_ID", "XML_API")
                temp_elem.set("UPDATE_APP_ID", "XML_API")
        
        # Update pressure profiles
        if 'pressureProfiles' in formation_inputs:
            for profile in formation_inputs['pressureProfiles']:
                # Different elements based on pressure type
                if profile['pressureType'] == 'Pore':
                    press_elem = ET.SubElement(export_elem, "CD_PORE_PRESSURE")
                elif profile['pressureType'] == 'Frac':
                    press_elem = ET.SubElement(export_elem, "CD_FRAC_PRESSURE")
                else:  # Hydrostatic
                    press_elem = ET.SubElement(export_elem, "CD_HYDROSTATIC_PRESSURE")
                
                # Set attributes
                press_elem.set("DEPTH", str(profile['depth']))
                press_elem.set("PRESSURE", str(profile['pressure']))
                if 'units' in profile:
                    press_elem.set("UNITS", profile['units'])
                
                # Add creation and update info
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                press_elem.set("CREATE_DATE", format_timestamp(now_str))
                press_elem.set("UPDATE_DATE", format_timestamp(now_str))
                press_elem.set("CREATE_USER_ID", "API_USER")
                press_elem.set("UPDATE_USER_ID", "API_USER")
                press_elem.set("CREATE_APP_ID", "XML_API")
                press_elem.set("UPDATE_APP_ID", "XML_API")
    
    def _update_casing_schematics(self, export_elem, casing_schematics):
        """
        Update casing schematics in the XML.
        
        Args:
            export_elem (Element): Export XML element
            casing_schematics (dict): Casing schematics
        """
        if not casing_schematics:
            return
        
        # Update materials
        if 'materials' in casing_schematics:
            for material in casing_schematics['materials']:
                mat_elem = ET.SubElement(export_elem, "CD_MATERIAL")
                
                # Set ID
                if 'materialId' in material:
                    mat_elem.set("MATERIAL_ID", material['materialId'])
                
                # Set other attributes
                for key, value in material.items():
                    if key != 'materialId':  # Skip the ID field
                        xml_key = convert_camel_to_xml_key(key)
                        mat_elem.set(xml_key, str(value))
                
                # Add creation and update info
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                mat_elem.set("CREATE_DATE", format_timestamp(now_str))
                mat_elem.set("UPDATE_DATE", format_timestamp(now_str))
                mat_elem.set("CREATE_USER_ID", "API_USER")
                mat_elem.set("UPDATE_USER_ID", "API_USER")
                mat_elem.set("CREATE_APP_ID", "XML_API")
                mat_elem.set("UPDATE_APP_ID", "XML_API")
        
        # Update assemblies
        if 'assemblies' in casing_schematics:
            for assembly in casing_schematics['assemblies']:
                # Create assembly element
                assembly_elem = ET.SubElement(export_elem, "CD_ASSEMBLY")
                
                # Set IDs
                if 'assemblyId' in assembly:
                    assembly_elem.set("ASSEMBLY_ID", assembly['assemblyId'])
                if 'wellboreId' in assembly:
                    assembly_elem.set("WELLBORE_ID", assembly['wellboreId'])
                
                # Get wellId from relationships
                if 'wellboreId' in assembly:
                    for parent_type, parent_id, child_type in self.id_registry.relationship_map:
                        if parent_type == 'WELL' and child_type == 'WELLBORE' and assembly['wellboreId'] in self.id_registry.relationship_map[(parent_type, parent_id, child_type)]:
                            assembly_elem.set("WELL_ID", parent_id)
                            break
                
                # Set other attributes
                for key, value in assembly.items():
                    if key not in ['assemblyId', 'wellboreId', 'components']:
                        xml_key = convert_camel_to_xml_key(key)
                        assembly_elem.set(xml_key, str(value))
                
                # Convert snake_case to appropriate format
                if 'topDepth' in assembly:
                    assembly_elem.set("MD_ASSEMBLY_TOP", str(assembly['topDepth']))
                if 'baseDepth' in assembly:
                    assembly_elem.set("MD_ASSEMBLY_BASE", str(assembly['baseDepth']))
                if 'topDepth' in assembly:
                    assembly_elem.set("MD_TOC", str(assembly['topDepth']))
                
                # Add creation and update info
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                assembly_elem.set("CREATE_DATE", format_timestamp(now_str))
                assembly_elem.set("UPDATE_DATE", format_timestamp(now_str))
                assembly_elem.set("CREATE_USER_ID", "API_USER")
                assembly_elem.set("UPDATE_USER_ID", "API_USER")
                assembly_elem.set("CREATE_APP_ID", "XML_API")
                assembly_elem.set("UPDATE_APP_ID", "XML_API")
                assembly_elem.set("IS_TOP_DOWN", "Y")
                
                # Update components
                if 'components' in assembly:
                    for i, component in enumerate(assembly['components']):
                        # Create component element
                        comp_elem = ET.SubElement(export_elem, "CD_ASSEMBLY_COMP")
                        
                        # Set IDs
                        if 'componentId' in component:
                            comp_elem.set("ASSEMBLY_COMP_ID", component['componentId'])
                        if 'assemblyId' in assembly:
                            comp_elem.set("ASSEMBLY_ID", assembly['assemblyId'])
                        if 'wellboreId' in assembly:
                            comp_elem.set("WELLBORE_ID", assembly['wellboreId'])
                        if "WELL_ID" in assembly_elem.attrib:
                            comp_elem.set("WELL_ID", assembly_elem.get("WELL_ID"))
                        
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
                        
                        # Set other attributes with appropriate naming conversion
                        for key, value in component.items():
                            if key not in ['componentId', 'assemblyId', 'wellboreId', 'componentType']:
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
                        
                        # Add creation and update info
                        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        comp_elem.set("CREATE_DATE", format_timestamp(now_str))
                        comp_elem.set("UPDATE_DATE", format_timestamp(now_str))
                        comp_elem.set("CREATE_USER_ID", "API_USER")
                        comp_elem.set("UPDATE_USER_ID", "API_USER")
                        comp_elem.set("CREATE_APP_ID", "XML_API")
                        comp_elem.set("UPDATE_APP_ID", "XML_API")