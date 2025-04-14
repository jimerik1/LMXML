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
        """
        try:
            # Read the file content to extract processing instructions
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract DataServices PI if present
                import re
                ds_match = re.search(r'<\?DataServices[^>]*\?>', content)
                if ds_match:
                    self.dataservices_pi = ds_match.group(0)
            
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
        """
        # Get the XML string with pretty printing
        xml_string = ET.tostring(self.root, encoding='utf-8', xml_declaration=True, pretty_print=True).decode('utf-8')
        
        # Always replace the XML declaration with the standard format including standalone attribute
        xml_string = xml_string.replace('<?xml version="1.0" encoding="utf-8"?>', 
                                    '<?xml version="1.0" standalone="no"?><?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>')
                
        # Check if DataServices PI is already present
        if '<?DataServices' not in xml_string:
            # Insert after XML declaration
            xml_string = xml_string.replace('<?xml version="1.0" standalone="no"?>', 
                                        '<?xml version="1.0" standalone="no"?>\n' + '<?xml version="1.0" standalone="no"?><?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>')
        
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
        """
        try:
            print(f"Updating temperature profiles for group {temp_group_id}")
            
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
            
            # Find the parent element where we'll insert new temperature gradients
            # This should be after the temperature gradient group
            group_xpath = f".//CD_TEMP_GRADIENT_GROUP[@TEMP_GRADIENT_GROUP_ID='{temp_group_id}']"
            group_elements = self.root.xpath(group_xpath)
            
            # Get the parent of the group to insert after it
            parent_elem = None
            if group_elements:
                parent_elem = group_elements[0].getparent()
            
            # If we couldn't find a parent, use the root
            if parent_elem is None:
                parent_elem = self.root
            
            # Add new temperature gradient elements for depths > 0
            for i, profile in enumerate(temp_profiles):
                if profile.get('depth', 0) > 0:
                    # Generate a new ID for each gradient element
                    temp_id = f"TEMP_{i:04d}"
                    
                    # Create element
                    element = ET.Element('CD_TEMP_GRADIENT')
                    element.set('WELL_ID', well_id)
                    element.set('WELLBORE_ID', wellbore_id)
                    element.set('TEMP_GRADIENT_GROUP_ID', temp_group_id)
                    element.set('TEMP_GRADIENT_ID', temp_id)
                    element.set('TEMPERATURE', str(profile.get('temperature')))
                    element.set('TVD', str(profile.get('depth')))
                    
                    # Add to parent
                    parent_elem.append(element)
                    
                    print(f"Added new temperature gradient at depth {profile.get('depth')}: {profile.get('temperature')}°F")
            
            return True
        except Exception as e:
            print(f"Error updating temperature profiles: {str(e)}")
            return False
    
    def update_pressure_profiles(self, well_id, wellbore_id, pore_group_id, frac_group_id, pressure_profiles):
        """
        Update pressure profiles in the XML.
        """
        try:
            print(f"Updating pressure profiles")
            
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
            
            # Find the pore pressure group to insert after
            pore_parent = self.root
            pore_group_xpath = f".//CD_PORE_PRESSURE_GROUP[@PORE_PRESSURE_GROUP_ID='{pore_group_id}']"
            pore_group_elements = self.root.xpath(pore_group_xpath)
            if pore_group_elements:
                pore_parent = pore_group_elements[0].getparent()
            
            # Find the frac gradient group to insert after
            frac_parent = self.root
            frac_group_xpath = f".//CD_FRAC_GRADIENT_GROUP[@FRAC_GRADIENT_GROUP_ID='{frac_group_id}']"
            frac_group_elements = self.root.xpath(frac_group_xpath)
            if frac_group_elements:
                frac_parent = frac_group_elements[0].getparent()
            
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
                
                # Create element
                element = ET.Element('CD_PORE_PRESSURE')
                element.set('WELL_ID', well_id)
                element.set('WELLBORE_ID', wellbore_id)
                element.set('PORE_PRESSURE_GROUP_ID', pore_group_id)
                element.set('PORE_PRESSURE_ID', pressure_id)
                element.set('PORE_PRESSURE', str(profile.get('pressure')))
                element.set('TVD', str(profile.get('depth')))
                element.set('IS_PERMEABLE_ZONE', 'Y')
                element.set('PORE_PRESSURE_EMW', str(emw) if emw is not None else '0.0')
                
                # Add to parent
                pore_parent.append(element)
                
                print(f"Added new pore pressure at depth {profile.get('depth')}: {profile.get('pressure')} {profile.get('units')}")
            
            # Add frac gradient elements (if any)
            for i, profile in enumerate(frac_pressures):
                # Generate a new ID for each element
                gradient_id = f"FRAC_{i:04d}"
                
                # Calculate EMW if not provided
                emw = profile.get('emw')
                if emw is None and profile.get('depth', 0) > 0:
                    pressure = profile.get('pressure', 0)
                    depth = profile.get('depth', 0)
                    emw = pressure / (0.052 * depth)
                
                # Create element
                element = ET.Element('CD_FRAC_GRADIENT')
                element.set('WELL_ID', well_id)
                element.set('WELLBORE_ID', wellbore_id)
                element.set('FRAC_GRADIENT_GROUP_ID', frac_group_id)
                element.set('FRAC_GRADIENT_ID', gradient_id)
                element.set('FRAC_GRADIENT_PRESSURE', str(profile.get('pressure')))
                element.set('TVD', str(profile.get('depth')))
                element.set('FRAC_GRADIENT_EMW', str(emw) if emw is not None else '0.0')
                
                # Add to parent
                frac_parent.append(element)
                
                print(f"Added new frac gradient at depth {profile.get('depth')}: {profile.get('pressure')} {profile.get('units')}")
            
            return True
        except Exception as e:
            print(f"Error updating pressure profiles: {str(e)}")
            return False

    def update_dls_overrides(self, well_id, wellbore_id, scenario_id, dls_group_id, dls_overrides):
        """
        Update dogleg severity overrides in the XML.
        """
        try:
            print(f"Updating DLS overrides for group {dls_group_id}")
            
            # First, remove existing DLS override entries
            xpath = f".//TU_DLS_OVERRIDE[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']"
            elements = self.root.xpath(xpath)
            for element in elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
            
            # Find the parent element where we'll insert new DLS overrides
            parent_elem = self.root
            group_xpath = f".//TU_DLS_OVERRIDE_GROUP[@DLS_OVERRIDE_GROUP_ID='{dls_group_id}']"
            group_elements = self.root.xpath(group_xpath)
            if group_elements:
                parent_elem = group_elements[0].getparent()
            
            # Add new DLS override elements
            for i, override in enumerate(dls_overrides):
                # Generate a new ID for each override
                override_id = f"DLS_{i:04d}"
                
                # Create the element
                element = ET.Element('TU_DLS_OVERRIDE')
                element.set('WELL_ID', well_id)
                element.set('WELLBORE_ID', wellbore_id)
                element.set('SCENARIO_ID', scenario_id)
                element.set('DLS_OVERRIDE_GROUP_ID', dls_group_id)
                element.set('DLS_OVERRIDE_ID', override_id)
                element.set('MD_TOP', str(override.get('topDepth')))
                element.set('MD_BASE', str(override.get('baseDepth')))
                element.set('DOGLEG_SEVERITY', str(override.get('doglegSeverity')))
                
                # Add creation and update info
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                element.set('CREATE_DATE', f"{{ts '{now}'}}")
                element.set('CREATE_USER_ID', 'API_USER')
                element.set('CREATE_APP_ID', 'XML_API')
                element.set('UPDATE_DATE', f"{{ts '{now}'}}")
                element.set('UPDATE_USER_ID', 'API_USER')
                element.set('UPDATE_APP_ID', 'XML_API')
                
                # Add to parent
                parent_elem.append(element)
                
                print(f"Added new DLS override: {override.get('topDepth')}-{override.get('baseDepth')}, DLS={override.get('doglegSeverity')}")
            
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
    
    def inject_binary_data(self):
        """
        Inject binary data from binary_data_library.xml into the XML.
        """
        try:
            # Get the template directory path
            template_dir = os.path.dirname(self.template_path)
            
            # Set the binary data library path
            binary_data_path = os.path.join(template_dir, 'binary_data_library.xml')
            
            print(f"Looking for binary data at {binary_data_path}")
            
            if not os.path.exists(binary_data_path):
                print(f"Warning: Binary data library not found at {binary_data_path}")
                return
            
            # Load binary data library
            binary_tree = ET.parse(binary_data_path)
            binary_root = binary_tree.getroot()
            
            # Find the BINARY_DATA element
            binary_data_elem = binary_root if binary_root.tag == 'BINARY_DATA' else binary_root.find(".//BINARY_DATA")
            
            if binary_data_elem is not None:
                print("Found BINARY_DATA element in binary data library")
                
                # Check if there's already a BINARY_DATA element in our XML
                existing_binary = self.root.find(".//BINARY_DATA")
                if existing_binary is not None:
                    print("Removing existing BINARY_DATA element")
                    parent = existing_binary.getparent()
                    if parent is not None:
                        parent.remove(existing_binary)
                
                # Create a new BINARY_DATA element in the export element
                binary_elem = ET.Element("BINARY_DATA")
                
                # Copy attributes
                for key, value in binary_data_elem.attrib.items():
                    binary_elem.set(key, value)
                
                # Get existing IDs from our XML
                well_ids = []
                wellbore_ids = []
                scenario_ids = []
                site_ids = []
                project_ids = ['dzwLFOVy7l']  # Hard-coded from your template
                policy_ids = ['Pzrgw9f4JC']   # Hard-coded from your template
                
                # Extract existing IDs
                for well_elem in self.root.xpath(".//CD_WELL"):
                    well_ids.append(well_elem.get('WELL_ID'))
                
                for wellbore_elem in self.root.xpath(".//CD_WELLBORE"):
                    wellbore_ids.append(wellbore_elem.get('WELLBORE_ID'))
                
                for scenario_elem in self.root.xpath(".//CD_SCENARIO"):
                    scenario_ids.append(scenario_elem.get('SCENARIO_ID'))
                
                for site_elem in self.root.xpath(".//CD_SITE"):
                    site_ids.append(site_elem.get('SITE_ID'))
                
                print(f"Found IDs in XML: well_ids={well_ids}, wellbore_ids={wellbore_ids}, scenario_ids={scenario_ids}, site_ids={site_ids}")
                
                # Process each attachment journal
                for journal_elem in binary_data_elem.findall("./CD_ATTACHMENT_JOURNAL"):
                    print("Processing CD_ATTACHMENT_JOURNAL element")
                    
                    # Create a new journal element
                    new_journal = ET.Element("CD_ATTACHMENT_JOURNAL")
                    
                    # Generate new IDs for the attachments
                    import random
                    import string
                    chars = string.ascii_letters + string.digits
                    attachment_id = ''.join(random.choice(chars) for _ in range(8))
                    attachment_journal_id = ''.join(random.choice(chars) for _ in range(8))
                    
                    # Copy and update attributes
                    for key, value in journal_elem.attrib.items():
                        if key == "ATTACHMENT_ID":
                            new_journal.set(key, attachment_id)
                        elif key == "ATTACHMENT_JOURNAL_ID":
                            new_journal.set(key, attachment_journal_id)
                        elif key == "ATTACHMENT_LOCATOR":
                            # Handle the composite locator string
                            locator = value
                            
                            # Create a new locator with our IDs
                            parts = {}
                            for part in locator.split('+'):
                                if '=' in part:
                                    name, id_value = part.split('=', 1)
                                    # Strip parentheses
                                    if id_value.startswith('(') and id_value.endswith(')'):
                                        id_value = id_value[1:-1]
                                    parts[name] = id_value
                            
                            # Update with our IDs but keep policy_id constant
                            if policy_ids:
                                parts['POLICY_ID'] = policy_ids[0]
                            if project_ids:
                                parts['PROJECT_ID'] = project_ids[0]
                            if site_ids:
                                parts['SITE_ID'] = site_ids[0]
                            if well_ids:
                                parts['WELL_ID'] = well_ids[0]
                            if wellbore_ids:
                                parts['WELLBORE_ID'] = wellbore_ids[0]
                            if scenario_ids:
                                parts['SCENARIO_ID'] = scenario_ids[0]
                            
                            # Reconstruct the locator string
                            new_locator = '+'.join([f"{name}=({value})" for name, value in parts.items()])
                            
                            new_journal.set(key, new_locator)
                        else:
                            new_journal.set(key, value)
                    
                    # Process the child CD_ATTACHMENT element
                    for attachment_elem in journal_elem.findall("./CD_ATTACHMENT"):
                        new_attachment = ET.Element("CD_ATTACHMENT")
                        
                        # Copy and update attributes
                        for key, value in attachment_elem.attrib.items():
                            if key == "ATTACHMENT_ID":
                                new_attachment.set(key, attachment_id)
                            else:
                                new_attachment.set(key, value)
                        
                        # Copy the binary data content
                        if attachment_elem.text:
                            new_attachment.text = attachment_elem.text
                        
                        # Copy any children of the attachment (if any)
                        for child in attachment_elem:
                            new_child = ET.fromstring(ET.tostring(child))
                            new_attachment.append(new_child)
                        
                        new_journal.append(new_attachment)
                    
                    # Copy other content and trailing text (the binary data)
                    if journal_elem.text and journal_elem.text.strip():
                        new_journal.text = journal_elem.text
                    
                    # Copy the text after the attachment element (often binary data)
                    if len(journal_elem) > 0 and journal_elem[-1].tail and journal_elem[-1].tail.strip():
                        for i, child in enumerate(new_journal):
                            if i == len(new_journal) - 1:  # Last child
                                child.tail = journal_elem[-1].tail
                    
                    # Add the journal to the binary element
                    binary_elem.append(new_journal)
                
                # Add the binary element to the root
                self.root.append(binary_elem)
                print("Binary data injected successfully")
                
                return True
            else:
                print("Warning: No BINARY_DATA element found in binary data library")
                return False
        except Exception as e:
            print(f"Error injecting binary data: {str(e)}")
            return False

    
    def update_from_payload(self, payload, add_binary_data=False):
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
        
            # Add binary data from template:
            if add_binary_data:
                print("Adding binary data to the XML")
                self.inject_binary_data()
                    
            print("Template update from payload completed successfully")
            return True

        except Exception as e:
            print(f"Error updating from payload: {str(e)}")
            return False
                                                  