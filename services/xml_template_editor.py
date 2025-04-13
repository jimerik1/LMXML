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
            print(f"Successfully loaded template from {template_path}")
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
            print(f"Successfully saved XML to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving XML: {str(e)}")
            return False
    
    def get_xml_string(self):
        """
        Get the XML as a string with proper formatting.
        
        Returns:
            str: XML as a string with proper line breaks
        """
        # Get the XML string with pretty printing
        xml_string = ET.tostring(self.root, encoding='utf-8', xml_declaration=True, pretty_print=True).decode('utf-8')
        
        # Use regex to ensure each XML tag is on a new line
        import re
        # This pattern will find closing tags followed immediately by opening tags
        pattern = r'(/>|>)(<)'
        # Replace with a closing tag, newline, then opening tag
        xml_string = re.sub(pattern, r'\1\n\2', xml_string)
        
        # Ensure DataServices processing instruction is preserved if it exists
        if '<?DataServices' not in xml_string and hasattr(self, 'dataservices_pi'):
            xml_string = xml_string.replace('<?xml version="1.0" encoding="utf-8"?>', 
                                        '<?xml version="1.0" encoding="utf-8"?>\n' + self.dataservices_pi)
        
        return xml_string
    
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
            print(f"No elements found for xpath: {xpath}")
            return False
        
        for element in elements:
            element.set(attr_name, str(attr_value))
            print(f"Updated attribute {attr_name}={attr_value} for element {tag_name}")
            
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
        
        result = self.update_element_attribute(tag_name, id_attr, id_value, name_attr, name_value)
        if result:
            print(f"Updated {name_attr} to '{name_value}' for {tag_name} with {id_attr}={id_value}")
        return result
    
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
        print(f"Created new element {tag_name} with attributes: {attributes}")
        return element
    
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
            print(f"Updating temperature profiles for group {temp_group_id}")
            print(f"Input profiles: {temp_profiles}")
            
            # First, remove existing temperature gradient entries
            xpath = f".//CD_TEMP_GRADIENT[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']"
            elements = self.root.xpath(xpath)
            print(f"Found {len(elements)} existing temperature gradients to remove")
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
                    print(f"Removed temperature gradient element with ID: {element.get('TEMP_GRADIENT_ID')}")
            
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
                    print(f"Updated surface temperature to {surface_temp} for group {temp_group_id}")
                else:
                    print(f"Warning: Temperature gradient group with ID {temp_group_id} not found")
            
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
                    
                    # Find the correct place to insert the element
                    # Typically after other temperature gradient elements or after the temperature gradient group
                    group_xpath = f".//CD_TEMP_GRADIENT_GROUP[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']"
                    group_elements = self.root.xpath(group_xpath)
                    
                    if group_elements:
                        # Insert after the group element
                        parent = group_elements[0].getparent()
                        if parent is not None:
                            index = parent.index(group_elements[0])
                            parent.insert(index + 1, element)
                            print(f"Added new temperature gradient at depth {profile.get('depth')}: {profile.get('temperature')}°F")
                        else:
                            # Fallback - just append to root
                            self.root.append(element)
                            print(f"Added new temperature gradient to root (fallback)")
                    else:
                        # Fallback - just append to root
                        self.root.append(element)
                        print(f"Added new temperature gradient to root (fallback)")
            
            print("Temperature profiles update completed successfully")
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
            print(f"Updating pressure profiles")
            print(f"Input profiles: {pressure_profiles}")
            
            # First, remove existing pressure entries
            for tag in ['CD_PORE_PRESSURE', 'CD_FRAC_GRADIENT']:
                xpath = f".//{tag}"
                elements = self.root.xpath(xpath)
                print(f"Found {len(elements)} existing {tag} elements to remove")
                for element in elements:
                    parent = element.getparent()
                    if parent is not None:
                        parent.remove(element)
                        print(f"Removed {tag} element")
            
            # Group pressure profiles by type
            pore_pressures = []
            frac_pressures = []
            
            for profile in pressure_profiles:
                pressure_type = profile.get('pressureType', '')
                if pressure_type == 'Pore':
                    pore_pressures.append(profile)
                elif pressure_type == 'Frac':
                    frac_pressures.append(profile)
            
            # Find the correct place to insert the elements
            pore_group_xpath = f".//CD_PORE_PRESSURE_GROUP[@PORE_PRESSURE_GROUP_ID='{pore_group_id}']"
            pore_group_elements = self.root.xpath(pore_group_xpath)
            
            frac_group_xpath = f".//CD_FRAC_GRADIENT_GROUP[@FRAC_GRADIENT_GROUP_ID='{frac_group_id}']"
            frac_group_elements = self.root.xpath(frac_group_xpath)
            
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
                
                # Create the element
                element = self.create_element('CD_PORE_PRESSURE', attributes)
                
                if pore_group_elements:
                    # Insert after the group element
                    parent = pore_group_elements[0].getparent()
                    if parent is not None:
                        index = parent.index(pore_group_elements[0])
                        parent.insert(index + 1, element)
                        print(f"Added new pore pressure at depth {profile.get('depth')}: {profile.get('pressure')} {profile.get('units')}")
                    else:
                        # Fallback - just append to root
                        self.root.append(element)
                        print(f"Added new pore pressure to root (fallback)")
                else:
                    # Fallback - just append to root
                    self.root.append(element)
                    print(f"Added new pore pressure to root (fallback) - group not found")
            
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
                
                # Create the element
                element = self.create_element('CD_FRAC_GRADIENT', attributes)
                
                if frac_group_elements:
                    # Insert after the group element
                    parent = frac_group_elements[0].getparent()
                    if parent is not None:
                        index = parent.index(frac_group_elements[0])
                        parent.insert(index + 1, element)
                        print(f"Added new frac gradient at depth {profile.get('depth')}: {profile.get('pressure')} {profile.get('units')}")
                    else:
                        # Fallback - just append to root
                        self.root.append(element)
                        print(f"Added new frac gradient to root (fallback)")
                else:
                    # Fallback - just append to root
                    self.root.append(element)
                    print(f"Added new frac gradient to root (fallback) - group not found")
            
            print("Pressure profiles update completed successfully")
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
            print(f"Updating DLS overrides for group {dls_group_id}")
            print(f"Input overrides: {dls_overrides}")
            
            # First, remove existing DLS override entries
            xpath = f".//TU_DLS_OVERRIDE[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']"
            elements = self.root.xpath(xpath)
            print(f"Found {len(elements)} existing DLS overrides to remove")
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
                    print(f"Removed DLS override element with ID: {element.get('DLS_OVERRIDE_ID')}")
            
            # Find the correct place to insert the elements
            group_xpath = f".//TU_DLS_OVERRIDE_GROUP[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']"
            group_elements = self.root.xpath(group_xpath)
            
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
                
                # Create the element
                element = self.create_element('TU_DLS_OVERRIDE', attributes)
                
                if group_elements:
                    # Insert after the group element
                    parent = group_elements[0].getparent()
                    if parent is not None:
                        index = parent.index(group_elements[0])
                        parent.insert(index + 1, element)
                        print(f"Added new DLS override: {override.get('topDepth')}-{override.get('baseDepth')}, DLS={override.get('doglegSeverity')}")
                    else:
                        # Fallback - just append to root
                        self.root.append(element)
                        print(f"Added new DLS override to root (fallback)")
                else:
                    # Fallback - just append to root
                    self.root.append(element)
                    print(f"Added new DLS override to root (fallback) - group not found")
            
            print("DLS overrides update completed successfully")
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
            print(f"Updating survey stations for header {survey_header_id}")
            print(f"Input stations: {survey_stations}")
            
            # First, remove existing survey station entries
            xpath = f".//CD_DEFINITIVE_SURVEY_STATION[@DEF_SURVEY_HEADER_ID='{survey_header_id}']"
            elements = self.root.xpath(xpath)
            print(f"Found {len(elements)} existing survey stations to remove")
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
                    print(f"Removed survey station element with ID: {element.get('DEFINITIVE_SURVEY_ID')}")
            
            # Update the header name if provided
            header_xpath = f".//CD_DEFINITIVE_SURVEY_HEADER[@DEF_SURVEY_HEADER_ID='{survey_header_id}']"
            header_elements = self.root.xpath(header_xpath)
            if header_elements and survey_stations and 'name' in survey_stations[0].get('name', {}):
                header_elements[0].set('NAME', survey_stations[0]['name'])
                print(f"Updated survey header name to: {survey_stations[0]['name']}")
            
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
                    'DATA_ENTRY_MODE': str(station.get('dataEntryMode', '0'))
                }
                
                # Add optional attributes if provided
                if 'tvd' in station:
                    attributes['TVD'] = str(station['tvd'])
                if 'doglegSeverity' in station:
                    attributes['DOGLEG_SEVERITY'] = str(station['doglegSeverity'])
                
                # Create the element
                element = self.create_element('CD_DEFINITIVE_SURVEY_STATION', attributes)
                
                if header_elements:
                    # Insert after the header element
                    parent = header_elements[0].getparent()
                    if parent is not None:
                        index = parent.index(header_elements[0])
                        parent.insert(index + 1, element)
                        print(f"Added new survey station at MD {station.get('md')}: AZ={station.get('azimuth')}, INC={station.get('inclination')}")
                    else:
                        # Fallback - just append to root
                        self.root.append(element)
                        print(f"Added new survey station to root (fallback)")
                else:
                    # Fallback - just append to root
                    self.root.append(element)
                    print(f"Added new survey station to root (fallback) - header not found")
            
            print("Survey stations update completed successfully")
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
            print("Starting template update from payload")
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
                print(f"Found site ID: {site_id}")
            
            # Find well element and extract ID
            well_elements = self.root.xpath(".//CD_WELL")
            if well_elements:
                well_id = well_elements[0].get('WELL_ID')
                print(f"Found well ID: {well_id}")
            
            # Find wellbore element and extract ID
            wellbore_elements = self.root.xpath(".//CD_WELLBORE")
            if wellbore_elements:
                wellbore_id = wellbore_elements[0].get('WELLBORE_ID')
                print(f"Found wellbore ID: {wellbore_id}")
            
            # Find scenario element and extract ID
            scenario_elements = self.root.xpath(".//CD_SCENARIO")
            if scenario_elements:
                scenario_id = scenario_elements[0].get('SCENARIO_ID')
                temp_gradient_group_id = scenario_elements[0].get('TEMP_GRADIENT_GROUP_ID')
                pore_pressure_group_id = scenario_elements[0].get('PORE_PRESSURE_GROUP_ID')
                frac_gradient_group_id = scenario_elements[0].get('FRAC_GRADIENT_GROUP_ID')
                survey_header_id = scenario_elements[0].get('DEF_SURVEY_HEADER_ID')
                datum_id = scenario_elements[0].get('DATUM_ID')
                print(f"Found scenario ID: {scenario_id}")
                print(f"Found temp group ID: {temp_gradient_group_id}")
                print(f"Found pore pressure group ID: {pore_pressure_group_id}")
                print(f"Found frac gradient group ID: {frac_gradient_group_id}")
                print(f"Found survey header ID: {survey_header_id}")
                print(f"Found datum ID: {datum_id}")
            
            # Find DLS override group and extract ID
            dls_group_elements = self.root.xpath(".//TU_DLS_OVERRIDE_GROUP")
            if dls_group_elements:
                dls_override_group_id = dls_group_elements[0].get('DLS_OVERRIDE_GROUP_ID')
                print(f"Found DLS override group ID: {dls_override_group_id}")
            
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
            
            print("Template update from payload completed successfully")
            return True
        except Exception as e:
            print(f"Error updating from payload: {str(e)}")
            return False
                                                  