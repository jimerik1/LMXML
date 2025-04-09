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
        
        # Update DLS overrides
        if 'formationInputs' in payload and 'dlsOverrideGroup' in payload['formationInputs']:
            self._update_dls_overrides(export_elem, payload['formationInputs']['dlsOverrideGroup'])
        
        # Update survey header and stations
        if 'formationInputs' in payload and 'surveyHeader' in payload['formationInputs']:
            self._update_survey_header(export_elem, payload['formationInputs']['surveyHeader'])
        
        # Update datum
        if 'datum' in payload:
            self._update_datum(export_elem, payload['datum'])
        
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
    
    def _prepare_ids(self, payload):
        """
        Generate and register IDs for entities in the payload.
        
        Args:
            payload (dict): Structured data payload
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
        
        # Handle DLS overrides
        formation_inputs = payload.get('formationInputs', {})
        dls_group = formation_inputs.get('dlsOverrideGroup', {})
        if dls_group:
            if not dls_group.get('groupId'):
                dls_group['groupId'] = self.id_registry.generate_id('DLS_OVERRIDE_GROUP')
            else:
                self.id_registry.register_entity('DLS_OVERRIDE_GROUP', dls_group['groupId'], dls_group)
            
            # Link to wellbore
            if wellbore and wellbore.get('wellboreId'):
                dls_group['wellboreId'] = wellbore['wellboreId']
                self.id_registry.register_relationship(
                    'WELLBORE', 
                    wellbore['wellboreId'], 
                    'DLS_OVERRIDE_GROUP', 
                    dls_group['groupId']
                )
            
            # DLS override IDs
            for override in dls_group.get('overrides', []):
                if not override.get('overrideId'):
                    override['overrideId'] = self.id_registry.generate_id('DLS_OVERRIDE')
                else:
                    self.id_registry.register_entity('DLS_OVERRIDE', override['overrideId'], override)
                
                self.id_registry.register_relationship(
                    'DLS_OVERRIDE_GROUP', 
                    dls_group['groupId'],
                    'DLS_OVERRIDE', 
                    override['overrideId']
                )
        
        # Handle survey header
        survey_header = formation_inputs.get('surveyHeader', {})
        if survey_header:
            if not survey_header.get('headerId'):
                survey_header['headerId'] = self.id_registry.generate_id('SURVEY_HEADER')
            else:
                self.id_registry.register_entity('SURVEY_HEADER', survey_header['headerId'], survey_header)
            
            # Link to wellbore
            if wellbore and wellbore.get('wellboreId'):
                survey_header['wellboreId'] = wellbore['wellboreId']
                self.id_registry.register_relationship(
                    'WELLBORE', 
                    wellbore['wellboreId'],
                    'SURVEY_HEADER', 
                    survey_header['headerId']
                )
            
            # Survey station IDs
            for station in survey_header.get('stations', []):
                if not station.get('stationId'):
                    station['stationId'] = self.id_registry.generate_id('SURVEY_STATION')
                else:
                    self.id_registry.register_entity('SURVEY_STATION', station['stationId'], station)
                
                self.id_registry.register_relationship(
                    'SURVEY_HEADER', 
                    survey_header['headerId'],
                    'SURVEY_STATION', 
                    station['stationId']
                )
        
        # Datum ID
        datum = payload.get('datum', {})
        if datum:
            if not datum.get('datumId'):
                datum['datumId'] = self.id_registry.generate_id('DATUM')
            else:
                self.id_registry.register_entity('DATUM', datum['datumId'], datum)
            
            # Link to well
            if well and well.get('wellId'):
                datum['wellId'] = well['wellId']
                self.id_registry.register_relationship(
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
            self._add_creation_info(site_elem)
        
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
            self._add_creation_info(well_elem)
        
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
            self._add_creation_info(wellbore_elem)
    
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
            # Create temperature gradient group
            temp_group_elem = ET.SubElement(export_elem, "CD_TEMP_GRADIENT_GROUP")
            temp_group_id = self.id_registry.generate_id('TEMP_GRADIENT_GROUP')
            temp_group_elem.set("TEMP_GRADIENT_GROUP_ID", temp_group_id)
            temp_group_elem.set("NAME", "Geothermal Gradient")
            temp_group_elem.set("PHASE", "PROTOTYPE")
            
            # Get wellbore ID from relationships
            for wellbore_id in self.id_registry.id_map.get('WELLBORE', []):
                temp_group_elem.set("WELLBORE_ID", wellbore_id)
                temp_group_elem.set("WELL_ID", self._get_parent_id('WELL', 'WELLBORE', wellbore_id))
                break
            
            # Add surface ambient temp if first profile is at depth 0
            surface_temp = None
            for profile in formation_inputs['temperatureProfiles']:
                if profile['depth'] == 0:
                    surface_temp = profile['temperature']
                    temp_group_elem.set("SURFACE_AMBIENT_TEMP", str(surface_temp))
                    break
            
            # Add creation info
            self._add_creation_info(temp_group_elem)
            
            # Add temperature profile points
            for profile in formation_inputs['temperatureProfiles']:
                if profile['depth'] > 0:  # Skip surface temp which is already in the group
                    temp_elem = ET.SubElement(export_elem, "CD_TEMP_GRADIENT")
                    temp_elem.set("TEMP_GRADIENT_GROUP_ID", temp_group_id)
                    temp_elem.set("TEMP_GRADIENT_ID", self.id_registry.generate_id('TEMP_GRADIENT'))
                    temp_elem.set("TEMPERATURE", str(profile['temperature']))
                    temp_elem.set("TVD", str(profile['depth']))
                    
                    # Add wellbore and well IDs
                    for wellbore_id in self.id_registry.id_map.get('WELLBORE', []):
                        temp_elem.set("WELLBORE_ID", wellbore_id)
                        temp_elem.set("WELL_ID", self._get_parent_id('WELL', 'WELLBORE', wellbore_id))
                        break
        
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
                pore_group_id = self.id_registry.generate_id('PORE_PRESSURE_GROUP')
                pore_group_elem.set("PORE_PRESSURE_GROUP_ID", pore_group_id)
                pore_group_elem.set("NAME", "Pore Pressure")
                pore_group_elem.set("PHASE", "PROTOTYPE")
                
                # Get wellbore ID from relationships
                for wellbore_id in self.id_registry.id_map.get('WELLBORE', []):
                    pore_group_elem.set("WELLBORE_ID", wellbore_id)
                    pore_group_elem.set("WELL_ID", self._get_parent_id('WELL', 'WELLBORE', wellbore_id))
                    break
                
                # Add creation info
                self._add_creation_info(pore_group_elem)
                
                # Add pore pressure points
                for pressure in pore_pressures:
                    press_elem = ET.SubElement(export_elem, "CD_PORE_PRESSURE")
                    press_elem.set("PORE_PRESSURE_GROUP_ID", pore_group_id)
                    press_elem.set("PORE_PRESSURE_ID", self.id_registry.generate_id('PORE_PRESSURE'))
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
                    for wellbore_id in self.id_registry.id_map.get('WELLBORE', []):
                        press_elem.set("WELLBORE_ID", wellbore_id)
                        press_elem.set("WELL_ID", self._get_parent_id('WELL', 'WELLBORE', wellbore_id))
                        break
            
            # Create frac gradient group if needed
            if frac_pressures:
                frac_group_elem = ET.SubElement(export_elem, "CD_FRAC_GRADIENT_GROUP")
                frac_group_id = self.id_registry.generate_id('FRAC_GRADIENT_GROUP')
                frac_group_elem.set("FRAC_GRADIENT_GROUP_ID", frac_group_id)
                frac_group_elem.set("NAME", "Frac Gradient")
                frac_group_elem.set("PHASE", "PROTOTYPE")
                
                # Get wellbore ID from relationships
                for wellbore_id in self.id_registry.id_map.get('WELLBORE', []):
                    frac_group_elem.set("WELLBORE_ID", wellbore_id)
                    frac_group_elem.set("WELL_ID", self._get_parent_id('WELL', 'WELLBORE', wellbore_id))
                    break
                
                # Add creation info
                self._add_creation_info(frac_group_elem)
                
                # Add frac pressure points
                for pressure in frac_pressures:
                    frac_elem = ET.SubElement(export_elem, "CD_FRAC_GRADIENT")
                    frac_elem.set("FRAC_GRADIENT_GROUP_ID", frac_group_id)
                    frac_elem.set("FRAC_GRADIENT_ID", self.id_registry.generate_id('FRAC_GRADIENT'))
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
                    for wellbore_id in self.id_registry.id_map.get('WELLBORE', []):
                        frac_elem.set("WELLBORE_ID", wellbore_id)
                        frac_elem.set("WELL_ID", self._get_parent_id('WELL', 'WELLBORE', wellbore_id))
                        break
    
    def _update_dls_overrides(self, export_elem, dls_override_group):
        """
        Update dogleg severity overrides in the XML.
        
        Args:
            export_elem (Element): Export XML element
            dls_override_group (dict): DLS override group
        """
        if not dls_override_group:
            return
        
        # Create group element
        group_elem = ET.SubElement(export_elem, "TU_DLS_OVERRIDE_GROUP")
        
        # Set attributes
        if 'groupId' in dls_override_group:
            group_elem.set("DLS_OVERRIDE_GROUP_ID", dls_override_group['groupId'])
        
        # Add well and wellbore IDs from relationships
        if 'wellboreId' in dls_override_group:
            group_elem.set("WELLBORE_ID", dls_override_group['wellboreId'])
            well_id = self._get_parent_id('WELL', 'WELLBORE', dls_override_group['wellboreId'])
            if well_id:
                group_elem.set("WELL_ID", well_id)
        
        # Add scenario ID if present
        if 'scenarioId' in dls_override_group:
            group_elem.set("SCENARIO_ID", dls_override_group['scenarioId'])
        
        # Add creation info
        self._add_creation_info(group_elem)
        
        # Add overrides
        for override in dls_override_group.get('overrides', []):
            override_elem = ET.SubElement(export_elem, "TU_DLS_OVERRIDE")
            
            if 'overrideId' in override:
                override_elem.set("DLS_OVERRIDE_ID", override['overrideId'])
            
            override_elem.set("DLS_OVERRIDE_GROUP_ID", dls_override_group.get('groupId', ''))
            
            if 'wellboreId' in dls_override_group:
                override_elem.set("WELLBORE_ID", dls_override_group['wellboreId'])
                well_id = self._get_parent_id('WELL', 'WELLBORE', dls_override_group['wellboreId'])
                if well_id:
                    override_elem.set("WELL_ID", well_id)
            
            if 'scenarioId' in dls_override_group:
                override_elem.set("SCENARIO_ID", dls_override_group['scenarioId'])
                
            # Set depth and severity values
            if 'topDepth' in override:
                override_elem.set("MD_TOP", str(override['topDepth']))
            if 'baseDepth' in override:
                override_elem.set("MD_BASE", str(override['baseDepth']))
            if 'doglegSeverity' in override:
                override_elem.set("DOGLEG_SEVERITY", str(override['doglegSeverity']))
            
            # Add creation and update info
            self._add_creation_info(override_elem)
    
    def _update_survey_header(self, export_elem, survey_header):
        """
        Update survey header and stations in the XML.
        
        Args:
            export_elem (Element): Export XML element
            survey_header (dict): Survey header
        """
        if not survey_header:
            return
        
        # Create header element
        header_elem = ET.SubElement(export_elem, "CD_DEFINITIVE_SURVEY_HEADER")
        
        # Set attributes
        if 'headerId' in survey_header:
            header_elem.set("DEF_SURVEY_HEADER_ID", survey_header['headerId'])
        
        # Set well and wellbore IDs
        if 'wellboreId' in survey_header:
            header_elem.set("WELLBORE_ID", survey_header['wellboreId'])
            well_id = self._get_parent_id('WELL', 'WELLBORE', survey_header['wellboreId'])
            if well_id:
                header_elem.set("WELL_ID", well_id)
        
        # Set other attributes
        for key, value in survey_header.items():
            if key not in ['headerId', 'wellboreId', 'stations']:
                xml_key = convert_camel_to_xml_key(key)
                header_elem.set(xml_key, str(value))
        
        # Add creation info
        self._add_creation_info(header_elem)
        
        # Add survey stations
        for station in survey_header.get('stations', []):
            station_elem = ET.SubElement(export_elem, "CD_DEFINITIVE_SURVEY_STATION")
            
            if 'stationId' in station:
                station_elem.set("DEFINITIVE_SURVEY_ID", station['stationId'])
            
            # Link to header
            station_elem.set("DEF_SURVEY_HEADER_ID", survey_header.get('headerId', ''))
            
            # Set station attributes
            for key, value in station.items():
                if key != 'stationId':
                    xml_key = convert_camel_to_xml_key(key)
                    station_elem.set(xml_key, str(value))
    
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
                
                # Add creation info
                self._add_creation_info(mat_elem)
        
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
                    well_id = self._get_parent_id('WELL', 'WELLBORE', assembly['wellboreId'])
                    if well_id:
                        assembly_elem.set("WELL_ID", well_id)
                
                # Set other attributes
                for key, value in assembly.items():
                    if key not in ['assemblyId', 'wellboreId', 'components']:
                        xml_key = convert_camel_to_xml_key(key)
                        assembly_elem.set(xml_key, str(value))
                
                # Convert snake_case to appropriate format
                if 'topDepth' in assembly:
                    assembly_elem.set("MD_ASSEMBLY_TOP", str(assembly['topDepth']))
                    assembly_elem.set("MD_TOC", str(assembly['topDepth']))
                if 'baseDepth' in assembly:
                    assembly_elem.set("MD_ASSEMBLY_BASE", str(assembly['baseDepth']))
                
                # Add creation info and standard flags
                self._add_creation_info(assembly_elem)
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
                        
                        # Add creation info
                        self._add_creation_info(comp_elem)
    
    def _update_datum(self, export_elem, datum):
        """
        Update datum information in the XML.
        
        Args:
            export_elem (Element): Export XML element
            datum (dict): Datum information
        """
        if not datum:
            return
        
        # Create datum element
        datum_elem = ET.SubElement(export_elem, "CD_DATUM")
        
        # Set attributes
        if 'datumId' in datum:
            datum_elem.set("DATUM_ID", datum['datumId'])
        
        if 'wellId' in datum:
            datum_elem.set("WELL_ID", datum['wellId'])
        
        # Set other attributes
        for key, value in datum.items():
            if key not in ['datumId', 'wellId']:
                xml_key = convert_camel_to_xml_key(key)
                datum_elem.set(xml_key, str(value))
        
        # Add creation info
        self._add_creation_info(datum_elem)
    
    def _add_creation_info(self, elem):
        """
        Add creation and update info to an element.
        
        Args:
            elem (Element): XML element
        """
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elem.set("CREATE_DATE", format_timestamp(now_str))
        elem.set("UPDATE_DATE", format_timestamp(now_str))
        elem.set("CREATE_USER_ID", "API_USER")
        elem.set("UPDATE_USER_ID", "API_USER")
        elem.set("CREATE_APP_ID", "XML_API")
        elem.set("UPDATE_APP_ID", "XML_API")
    
    def _get_parent_id(self, parent_type, child_type, child_id):
        """
        Find parent ID based on relationship.
        
        Args:
            parent_type (str): Type of parent entity
            child_type (str): Type of child entity
            child_id (str): ID of child entity
            
        Returns:
            str: Parent ID or None
        """
        for (p_type, p_id, c_type), child_ids in self.id_registry.relationship_map.items():
            if p_type == parent_type and c_type == child_type and child_id in child_ids:
                return p_id
        return None