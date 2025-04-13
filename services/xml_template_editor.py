# services/xml_template_editor.py
from lxml import etree as ET
import os
import re
from datetime import datetime

class XMLTemplateEditor:
    """
    Service for editing existing XML templates while preserving IDs and relationships.
    
    This editor allows for targeted updates to specific elements without changing
    the overall structure or IDs of the XML file.
    """
    
    def __init__(self, template_path=None):
        """Initialize the XML template editor with an optional template path."""
        self.template_path = template_path
        self.tree = None
        self.root = None
        if template_path and os.path.exists(template_path):
            self.load_template(template_path)
    
    def load_template(self, template_path):
        """
        Load an XML template from a file path.
        
        Args:
            template_path (str): Path to the XML template
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            self.template_path = template_path
            self.tree = ET.parse(template_path)
            self.root = self.tree.getroot()
            return True
        except Exception as e:
            print(f"Error loading XML template: {str(e)}")
            return False
    
    def save_to_file(self, output_path):
        """
        Save the modified XML to a file.
        
        Args:
            output_path (str): Path to save the XML file
            
        Returns:
            bool: True if successfully saved, False otherwise
        """
        try:
            self.tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
            return True
        except Exception as e:
            print(f"Error saving XML: {str(e)}")
            return False
    
    def get_xml_string(self):
        """
        Get the XML as a string.
        
        Returns:
            str: XML as a string
        """
        return ET.tostring(self.root, encoding='utf-8', xml_declaration=True, pretty_print=True).decode('utf-8')
    
    def update_element_attribute(self, tag_name, id_attr, id_value, attr_name, attr_value):
        """
        Update a specific attribute in an element identified by its tag and ID.
        
        Args:
            tag_name (str): Element tag name (e.g., 'CD_SITE')
            id_attr (str): ID attribute name (e.g., 'SITE_ID')
            id_value (str): ID attribute value to match
            attr_name (str): Attribute name to update
            attr_value (str): New attribute value
            
        Returns:
            bool: True if element was found and updated, False otherwise
        """
        xpath = f".//{tag_name}[@{id_attr}='{id_value}']"
        elements = self.root.xpath(xpath)
        
        if not elements:
            return False
        
        for element in elements:
            element.set(attr_name, str(attr_value))
            
            # Update the timestamp if it's an update date
            if attr_name not in ['CREATE_DATE', 'UPDATE_DATE']:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                element.set('UPDATE_DATE', f"{{ts '{now}'}}")
                element.set('UPDATE_USER_ID', 'API_USER')
                element.set('UPDATE_APP_ID', 'XML_API')
        
        return True
    
    def update_element_name(self, tag_name, id_attr, id_value, name_value):
        """
        Update the name attribute of an element identified by its tag and ID.
        
        Args:
            tag_name (str): Element tag name (e.g., 'CD_SITE')
            id_attr (str): ID attribute name (e.g., 'SITE_ID')
            id_value (str): ID attribute value to match
            name_value (str): New name value
            
        Returns:
            bool: True if element was found and updated, False otherwise
        """
        # Determine the name attribute based on the tag
        name_attr = 'NAME'
        if tag_name == 'CD_SITE':
            name_attr = 'SITE_NAME'
        elif tag_name == 'CD_WELL':
            name_attr = 'WELL_COMMON_NAME'
        elif tag_name == 'CD_WELLBORE':
            name_attr = 'WELLBORE_NAME'
        elif tag_name == 'CD_DATUM':
            name_attr = 'DATUM_NAME'
        elif tag_name == 'CD_ASSEMBLY':
            name_attr = 'ASSEMBLY_NAME'
        elif tag_name == 'CD_CASE':
            name_attr = 'CASE_NAME'
        
        return self.update_element_attribute(tag_name, id_attr, id_value, name_attr, name_value)
    
    def add_child_element(self, parent_tag, parent_id_attr, parent_id_value, child_element):
        """
        Add a child element to a parent element identified by its tag and ID.
        
        Args:
            parent_tag (str): Parent element tag name
            parent_id_attr (str): Parent ID attribute name
            parent_id_value (str): Parent ID attribute value to match
            child_element (Element): Child element to add
            
        Returns:
            bool: True if parent was found and child added, False otherwise
        """
        xpath = f".//{parent_tag}[@{parent_id_attr}='{parent_id_value}']"
        parents = self.root.xpath(xpath)
        
        if not parents:
            return False
        
        # Add to the parent element
        parents[0].append(child_element)
        return True
    
    def create_element(self, tag_name, attributes):
        """
        Create a new XML element with the specified attributes.
        
        Args:
            tag_name (str): Element tag name
            attributes (dict): Dictionary of attribute name-value pairs
            
        Returns:
            Element: The created element
        """
        element = ET.Element(tag_name)
        for attr, value in attributes.items():
            element.set(attr, str(value))
        return element
    
    def remove_elements_by_tag(self, tag_name):
        """
        Remove all elements with a specific tag.
        
        Args:
            tag_name (str): Element tag name to remove
            
        Returns:
            int: Number of elements removed
        """
        elements = self.root.findall(f".//{tag_name}")
        count = 0
        
        for element in elements:
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
                count += 1
        
        return count
    
    def update_temperature_profiles(self, well_id, wellbore_id, temp_group_id, temp_profiles):
        """
        Update temperature profiles in the XML.
        
        Args:
            well_id (str): Well ID
            wellbore_id (str): Wellbore ID
            temp_group_id (str): Temperature gradient group ID
            temp_profiles (list): List of temperature profile dictionaries
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            # First, remove existing temperature gradient entries
            xpath = f".//CD_TEMP_GRADIENT[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']"
            elements = self.root.xpath(xpath)
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
            
            # Update surface temperature in the group if provided
            surface_temp = None
            for profile in temp_profiles:
                if profile.get('depth') == 0:
                    surface_temp = profile.get('temperature')
                    break
            
            if surface_temp is not None:
                group_xpath = f".//CD_TEMP_GRADIENT_GROUP[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']"
                group_elements = self.root.xpath(group_xpath)
                if group_elements:
                    group_elements[0].set('SURFACE_AMBIENT_TEMP', str(surface_temp))
            
            # Add new temperature gradient elements for depths > 0
            for i, profile in enumerate(temp_profiles):
                if profile.get('depth', 0) > 0:
                    # Generate a new ID for each gradient element
                    temp_id = f"TEMP_{i:04d}"
                    
                    # Create attributes
                    attributes = {
                        'WELL_ID': well_id,
                        'WELLBORE_ID': wellbore_id,
                        'TEMP_GRADIENT_GROUP_ID': temp_group_id,
                        'TEMP_GRADIENT_ID': temp_id,
                        'TEMPERATURE': str(profile.get('temperature')),
                        'TVD': str(profile.get('depth'))
                    }
                    
                    # Create and add the element
                    element = self.create_element('CD_TEMP_GRADIENT', attributes)
                    self.root.append(element)
            
            return True
        except Exception as e:
            print(f"Error updating temperature profiles: {str(e)}")
            return False
    
    def update_pressure_profiles(self, well_id, wellbore_id, pore_group_id, frac_group_id, pressure_profiles):
        """
        Update pressure profiles in the XML.
        
        Args:
            well_id (str): Well ID
            wellbore_id (str): Wellbore ID
            pore_group_id (str): Pore pressure group ID
            frac_group_id (str): Frac gradient group ID
            pressure_profiles (list): List of pressure profile dictionaries
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            # First, remove existing pressure entries
            for tag in ['CD_PORE_PRESSURE', 'CD_FRAC_GRADIENT']:
                xpath = f".//{tag}"
                elements = self.root.xpath(xpath)
                for element in elements:
                    parent = element.getparent()
                    if parent is not None:
                        parent.remove(element)
            
            # Group pressure profiles by type
            pore_pressures = []
            frac_pressures = []
            
            for profile in pressure_profiles:
                pressure_type = profile.get('pressureType', '')
                if pressure_type == 'Pore':
                    pore_pressures.append(profile)
                elif pressure_type == 'Frac':
                    frac_pressures.append(profile)
            
            # Add pore pressure elements
            for i, profile in enumerate(pore_pressures):
                # Generate a new ID for each element
                pressure_id = f"PORE_{i:04d}"
                
                # Calculate EMW if not provided
                emw = profile.get('emw')
                if emw is None and profile.get('depth', 0) > 0:
                    pressure = profile.get('pressure', 0)
                    depth = profile.get('depth', 0)
                    emw = pressure / (0.052 * depth)
                
                # Create attributes
                attributes = {
                    'WELL_ID': well_id,
                    'WELLBORE_ID': wellbore_id,
                    'PORE_PRESSURE_GROUP_ID': pore_group_id,
                    'PORE_PRESSURE_ID': pressure_id,
                    'PORE_PRESSURE': str(profile.get('pressure')),
                    'TVD': str(profile.get('depth')),
                    'IS_PERMEABLE_ZONE': profile.get('isPermeableZone', 'Y'),
                    'PORE_PRESSURE_EMW': str(emw) if emw is not None else '0.0'
                }
                
                # Create and add the element
                element = self.create_element('CD_PORE_PRESSURE', attributes)
                self.root.append(element)
            
            # Add frac gradient elements
            for i, profile in enumerate(frac_pressures):
                # Generate a new ID for each element
                gradient_id = f"FRAC_{i:04d}"
                
                # Calculate EMW if not provided
                emw = profile.get('emw')
                if emw is None and profile.get('depth', 0) > 0:
                    pressure = profile.get('pressure', 0)
                    depth = profile.get('depth', 0)
                    emw = pressure / (0.052 * depth)
                
                # Create attributes
                attributes = {
                    'WELL_ID': well_id,
                    'WELLBORE_ID': wellbore_id,
                    'FRAC_GRADIENT_GROUP_ID': frac_group_id,
                    'FRAC_GRADIENT_ID': gradient_id,
                    'FRAC_GRADIENT_PRESSURE': str(profile.get('pressure')),
                    'TVD': str(profile.get('depth')),
                    'FRAC_GRADIENT_EMW': str(emw) if emw is not None else '0.0'
                }
                
                # Create and add the element
                element = self.create_element('CD_FRAC_GRADIENT', attributes)
                self.root.append(element)
            
            return True
        except Exception as e:
            print(f"Error updating pressure profiles: {str(e)}")
            return False
    
    def update_dls_overrides(self, well_id, wellbore_id, scenario_id, dls_group_id, dls_overrides):
        """
        Update dogleg severity overrides in the XML.
        
        Args:
            well_id (str): Well ID
            wellbore_id (str): Wellbore ID
            scenario_id (str): Scenario ID
            dls_group_id (str): DLS override group ID
            dls_overrides (list): List of DLS override dictionaries
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            # First, remove existing DLS override entries
            xpath = f".//TU_DLS_OVERRIDE[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']"
            elements = self.root.xpath(xpath)
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
            
            # Add new DLS override elements
            for i, override in enumerate(dls_overrides):
                # Generate a new ID for each override
                override_id = f"DLS_{i:04d}"
                
                # Create attributes
                attributes = {
                    'WELL_ID': well_id,
                    'WELLBORE_ID': wellbore_id,
                    'SCENARIO_ID': scenario_id,
                    'DLS_OVERRIDE_GROUP_ID': dls_group_id,
                    'DLS_OVERRIDE_ID': override_id,
                    'MD_TOP': str(override.get('topDepth')),
                    'MD_BASE': str(override.get('baseDepth')),
                    'DOGLEG_SEVERITY': str(override.get('doglegSeverity'))
                }
                
                # Add creation and update info
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                attributes['CREATE_DATE'] = f"{{ts '{now}'}}"
                attributes['CREATE_USER_ID'] = 'API_USER'
                attributes['CREATE_APP_ID'] = 'XML_API'
                attributes['UPDATE_DATE'] = f"{{ts '{now}'}}"
                attributes['UPDATE_USER_ID'] = 'API_USER'
                attributes['UPDATE_APP_ID'] = 'XML_API'
                
                # Create and add the element
                element = self.create_element('TU_DLS_OVERRIDE', attributes)
                self.root.append(element)
            
            return True
        except Exception as e:
            print(f"Error updating DLS overrides: {str(e)}")
            return False
    
    def update_survey_stations(self, well_id, wellbore_id, survey_header_id, survey_stations):
        """
        Update survey stations in the XML.
        
        Args:
            well_id (str): Well ID
            wellbore_id (str): Wellbore ID
            survey_header_id (str): Survey header ID
            survey_stations (list): List of survey station dictionaries
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            # First, remove existing survey station entries
            xpath = f".//CD_DEFINITIVE_SURVEY_STATION[@DEF_SURVEY_HEADER_ID='{survey_header_id}']"
            elements = self.root.xpath(xpath)
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
            
            # Add new survey station elements
            for i, station in enumerate(survey_stations):
                # Generate a new ID for each station
                station_id = f"SURV_{i:04d}"
                
                # Create attributes
                attributes = {
                    'WELL_ID': well_id,
                    'WELLBORE_ID': wellbore_id,
                    'DEF_SURVEY_HEADER_ID': survey_header_id,
                    'DEFINITIVE_SURVEY_ID': station_id,
                    'AZIMUTH': str(station.get('azimuth')),
                    'INCLINATION': str(station.get('inclination')),
                    'MD': str(station.get('md')),
                    'SEQUENCE_NO': str(float(i)),
                    'DATA_ENTRY_MODE': station.get('dataEntryMode', '0')
                }
                
                # Add optional attributes if provided
                if 'tvd' in station:
                    attributes['TVD'] = str(station['tvd'])
                if 'doglegSeverity' in station:
                    attributes['DOGLEG_SEVERITY'] = str(station['doglegSeverity'])
                
                # Create and add the element
                element = self.create_element('CD_DEFINITIVE_SURVEY_STATION', attributes)
                self.root.append(element)
            
            return True
        except Exception as e:
            print(f"Error updating survey stations: {str(e)}")
            return False
    
    def update_from_payload(self, payload):
        """
        Update the XML template using data from a payload.
        
        Args:
            payload (dict): Payload data
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            # Extract key IDs from the template
            well_id = None
            wellbore_id = None
            site_id = None
            scenario_id = None
            temp_gradient_group_id = None
            pore_pressure_group_id = None
            frac_gradient_group_id = None
            dls_override_group_id = None
            survey_header_id = None
            datum_id = None
            
            # Find site element and extract ID
            site_elements = self.root.xpath(".//CD_SITE")
            if site_elements:
                site_id = site_elements[0].get('SITE_ID')
            
            # Find well element and extract ID
            well_elements = self.root.xpath(".//CD_WELL")
            if well_elements:
                well_id = well_elements[0].get('WELL_ID')
            
            # Find wellbore element and extract ID
            wellbore_elements = self.root.xpath(".//CD_WELLBORE")
            if wellbore_elements:
                wellbore_id = wellbore_elements[0].get('WELLBORE_ID')
            
            # Find scenario element and extract ID
            scenario_elements = self.root.xpath(".//CD_SCENARIO")
            if scenario_elements:
                scenario_id = scenario_elements[0].get('SCENARIO_ID')
                temp_gradient_group_id = scenario_elements[0].get('TEMP_GRADIENT_GROUP_ID')
                pore_pressure_group_id = scenario_elements[0].get('PORE_PRESSURE_GROUP_ID')
                frac_gradient_group_id = scenario_elements[0].get('FRAC_GRADIENT_GROUP_ID')
                survey_header_id = scenario_elements[0].get('DEF_SURVEY_HEADER_ID')
                datum_id = scenario_elements[0].get('DATUM_ID')
            
            # Find DLS override group and extract ID
            dls_group_elements = self.root.xpath(".//TU_DLS_OVERRIDE_GROUP")
            if dls_group_elements:
                dls_override_group_id = dls_group_elements[0].get('DLS_OVERRIDE_GROUP_ID')
            
            # Update project information
            project_info = payload.get('projectInfo', {})
            
            # Update site information
            if 'site' in project_info and site_id:
                site = project_info['site']
                if 'siteName' in site:
                    self.update_element_name('CD_SITE', 'SITE_ID', site_id, site['siteName'])
            
            # Update well information
            if 'well' in project_info and well_id:
                well = project_info['well']
                if 'wellCommonName' in well:
                    self.update_element_name('CD_WELL', 'WELL_ID', well_id, well['wellCommonName'])
            
            # Update wellbore information
            if 'wellbore' in project_info and wellbore_id:
                wellbore = project_info['wellbore']
                if 'wellboreName' in wellbore:
                    self.update_element_name('CD_WELLBORE', 'WELLBORE_ID', wellbore_id, wellbore['wellboreName'])
            
            # Update scenario name if provided
            if scenario_id and 'well' in project_info and 'wellCommonName' in project_info['well']:
                self.update_element_name('CD_SCENARIO', 'SCENARIO_ID', scenario_id, project_info['well']['wellCommonName'])
            
            # Update formation inputs
            formation_inputs = payload.get('formationInputs', {})
            
            # Update temperature profiles
            if 'temperatureProfiles' in formation_inputs and well_id and wellbore_id and temp_gradient_group_id:
                self.update_temperature_profiles(
                    well_id, 
                    wellbore_id,
                    temp_gradient_group_id, 
                    formation_inputs['temperatureProfiles']
                )
            
            # Update pressure profiles
            if 'pressureProfiles' in formation_inputs and well_id and wellbore_id and pore_pressure_group_id and frac_gradient_group_id:
                self.update_pressure_profiles(
                    well_id,
                    wellbore_id,
                    pore_pressure_group_id,
                    frac_gradient_group_id,
                    formation_inputs['pressureProfiles']
                )
            
            # Update DLS overrides
            if 'dlsOverrideGroup' in formation_inputs and 'overrides' in formation_inputs['dlsOverrideGroup'] and well_id and wellbore_id and scenario_id and dls_override_group_id:
                self.update_dls_overrides(
                    well_id,
                    wellbore_id,
                    scenario_id,
                    dls_override_group_id,
                    formation_inputs['dlsOverrideGroup']['overrides']
                )
            
            # Update survey header and stations
            if 'surveyHeader' in formation_inputs and 'stations' in formation_inputs['surveyHeader'] and well_id and wellbore_id and survey_header_id:
                self.update_survey_stations(
                    well_id,
                    wellbore_id,
                    survey_header_id,
                    formation_inputs['surveyHeader']['stations']
                )
            
            # Update datum
            if 'datum' in payload and datum_id:
                datum = payload['datum']
                if 'datumName' in datum:
                    self.update_element_name('CD_DATUM', 'DATUM_ID', datum_id, datum['datumName'])
                if 'datumElevation' in datum:
                    self.update_element_attribute('CD_DATUM', 'DATUM_ID', datum_id, 'DATUM_ELEVATION', datum['datumElevation'])
            
            return True
        except Exception as e:
            print(f"Error updating from payload: {str(e)}")
            return False