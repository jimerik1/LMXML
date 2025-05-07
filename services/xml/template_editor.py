# services/xml/template_editor.py
import logging
import os
import re
from typing import Dict, List, Any, Optional
from lxml import etree as ET

from services.xml.element_operations import (
    update_element_attribute, update_element_name, extract_entity_ids,
    update_project_info, update_datum
)
from services.xml.profile_handlers import (
    update_temperature_profiles, update_pressure_profiles
)
from services.xml.dls_handlers import update_dls_overrides
from services.xml.survey_handlers import update_survey_stations
from services.xml.binary_data import inject_binary_data
from services.xml.casing_handlers import update_casing_assemblies

logger = logging.getLogger(__name__)

class XMLTemplateEditor:
    """
    Service for editing existing XML templates while preserving IDs and relationships.
    
    This editor allows for targeted updates to specific elements without changing
    the overall structure or IDs of the XML file.
    """
    
    def __init__(self, template_path: Optional[str] = None):
        """Initialize the XML template editor with an optional template path."""
        self.template_path = template_path
        self.tree = None
        self.root = None
        self.dataservices_pi = None
        
        if template_path and os.path.exists(template_path):
            self.load_template(template_path)
    
    def load_template(self, template_path: str) -> bool:
        """
        Load an XML template from a file path.
        
        Args:
            template_path: Path to the XML template file
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            # Read the file content to extract processing instructions
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract DataServices PI if present
                ds_match = re.search(r'<\?DataServices[^>]*\?>', content)
                if ds_match:
                    self.dataservices_pi = ds_match.group(0)
            
            self.template_path = template_path
            self.tree = ET.parse(template_path)
            self.root = self.tree.getroot()
            logger.info(f"Successfully loaded template from {template_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading XML template: {str(e)}")
            return False
    
    def save_to_file(self, output_path: str) -> bool:
        """
        Save the modified XML to a file.
        
        Args:
            output_path: Path to save the XML file
            
        Returns:
            bool: True if successfully saved, False otherwise
        """
        try:
            self.tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
            logger.info(f"Successfully saved XML to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving XML: {str(e)}")
            return False
    
    def get_xml_string(self) -> str:
        """
        Get the XML as a string with proper formatting.
        
        Returns:
            str: Formatted XML string
        """
        # Get the XML string with pretty printing
        xml_string = ET.tostring(self.root, encoding='utf-8', xml_declaration=True, pretty_print=True).decode('utf-8')
        
        # Replace the XML declaration with the standard format including DataServices PI
        xml_string = xml_string.replace('<?xml version=\'1.0\' encoding=\'utf-8\'?>', 
                        '<?xml version="1.0" standalone="no"?>\n<?DataServices DB_Major_Version=14;DB_Minor_Version=00;DB_Build_Version=000;DB_Version=EDM 5000.14.0 (14.00.00.000);expandPoint=CD_SCENARIO;?>')
        
        return xml_string
    
    def update_element_attribute(self, tag_name: str, id_attr: str, id_value: str, 
                                attr_name: str, attr_value: Any) -> bool:
        """
        Update a specific attribute in an element identified by its tag and ID.
        
        Args:
            tag_name: Element tag name (e.g., 'CD_SITE')
            id_attr: ID attribute name (e.g., 'SITE_ID')
            id_value: ID attribute value to match
            attr_name: Attribute name to update
            attr_value: New attribute value
            
        Returns:
            bool: True if element was found and updated, False otherwise
        """
        return update_element_attribute(self.root, tag_name, id_attr, id_value, attr_name, attr_value)
    
    def update_element_name(self, tag_name: str, id_attr: str, id_value: str, name_value: str) -> bool:
        """
        Update the name attribute of an element identified by its tag and ID.
        
        Args:
            tag_name: Element tag name (e.g., 'CD_SITE')
            id_attr: ID attribute name (e.g., 'SITE_ID')
            id_value: ID attribute value to match
            name_value: New name value
            
        Returns:
            bool: True if element was found and updated, False otherwise
        """
        return update_element_name(self.root, tag_name, id_attr, id_value, name_value)
    
    def update_temperature_profiles(self, well_id: str, wellbore_id: str, 
                                    temp_group_id: str, temp_profiles: List[Dict[str, Any]]) -> bool:
        """
        Update temperature profiles in the XML.
        
        Args:
            well_id: Well ID
            wellbore_id: Wellbore ID
            temp_group_id: Temperature gradient group ID
            temp_profiles: List of temperature profile data
            
        Returns:
            bool: True if successful, False otherwise
        """
        return update_temperature_profiles(self.root, well_id, wellbore_id, 
                                          temp_group_id, temp_profiles)
    
    def update_pressure_profiles(self, well_id: str, wellbore_id: str, pore_group_id: str, 
                                frac_group_id: str, pressure_profiles: List[Dict[str, Any]]) -> bool:
        """
        Update pressure profiles in the XML.
        
        Args:
            well_id: Well ID
            wellbore_id: Wellbore ID
            pore_group_id: Pore pressure group ID
            frac_group_id: Frac gradient group ID
            pressure_profiles: List of pressure profile data
            
        Returns:
            bool: True if successful, False otherwise
        """
        return update_pressure_profiles(self.root, well_id, wellbore_id, 
                                       pore_group_id, frac_group_id, pressure_profiles)
    
    def update_dls_overrides(self, well_id: str, wellbore_id: str, scenario_id: str, 
                            dls_group_id: str, dls_overrides: List[Dict[str, Any]]) -> bool:
        """
        Update dogleg severity overrides in the XML.
        
        Args:
            well_id: Well ID
            wellbore_id: Wellbore ID
            scenario_id: Scenario ID
            dls_group_id: DLS override group ID
            dls_overrides: List of DLS override data
            
        Returns:
            bool: True if successful, False otherwise
        """
        return update_dls_overrides(self.root, well_id, wellbore_id, scenario_id, 
                                   dls_group_id, dls_overrides)
    
    def update_survey_stations(self, well_id: str, wellbore_id: str, 
                              survey_header_id: str, survey_stations: List[Dict[str, Any]]) -> bool:
        """
        Update survey stations in the XML.
        
        Args:
            well_id: Well ID
            wellbore_id: Wellbore ID
            survey_header_id: Survey header ID
            survey_stations: List of survey station data
            
        Returns:
            bool: True if successful, False otherwise
        """
        return update_survey_stations(self.root, well_id, wellbore_id, 
                                     survey_header_id, survey_stations)
    
    def update_casing_assemblies(self, well_id: str, wellbore_id: str,
                               assemblies: List[Dict[str, Any]]) -> bool:
        """
        Update casing assemblies and their components in the XML.
        
        Args:
            well_id: Well ID
            wellbore_id: Wellbore ID
            assemblies: List of assembly data
            
        Returns:
            bool: True if successful, False otherwise
        """
        return update_casing_assemblies(self.root, well_id, wellbore_id, assemblies)
    
    def update_from_payload(self, payload: Dict[str, Any], add_binary_data: bool = False) -> bool:
        """
        Update the XML template using data from a payload.
        
        Args:
            payload: Payload data dictionary
            add_binary_data: Whether to add binary data
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            logger.info("Starting template update from payload")
            
            # Extract key IDs from the template
            entity_ids = extract_entity_ids(self.root)
            
            # Update project information
            update_project_info(self.root, payload.get('projectInfo', {}), entity_ids)
            
            # Update formation inputs
            formation_inputs = payload.get('formationInputs', {})
            well_id = entity_ids['well_id']
            wellbore_id = entity_ids['wellbore_id']
            scenario_id = entity_ids['scenario_id']
            
            # Update temperature profiles
            if ('temperatureProfiles' in formation_inputs and well_id and 
                wellbore_id and entity_ids['temp_gradient_group_id']):
                self.update_temperature_profiles(
                    well_id, 
                    wellbore_id,
                    entity_ids['temp_gradient_group_id'], 
                    formation_inputs['temperatureProfiles']
                )
            
            # Update pressure profiles
            if ('pressureProfiles' in formation_inputs and well_id and wellbore_id and 
                entity_ids['pore_pressure_group_id'] and entity_ids['frac_gradient_group_id']):
                self.update_pressure_profiles(
                    well_id,
                    wellbore_id,
                    entity_ids['pore_pressure_group_id'],
                    entity_ids['frac_gradient_group_id'],
                    formation_inputs['pressureProfiles']
                )
            
            # Update DLS overrides
            if ('dlsOverrideGroup' in formation_inputs and 
                'overrides' in formation_inputs['dlsOverrideGroup'] and 
                well_id and wellbore_id and scenario_id and entity_ids['dls_override_group_id']):
                self.update_dls_overrides(
                    well_id,
                    wellbore_id,
                    scenario_id,
                    entity_ids['dls_override_group_id'],
                    formation_inputs['dlsOverrideGroup']['overrides']
                )
            
            # Update survey header and stations
            if ('surveyHeader' in formation_inputs and 
                'stations' in formation_inputs['surveyHeader'] and 
                well_id and wellbore_id and entity_ids['survey_header_id']):
                self.update_survey_stations(
                    well_id,
                    wellbore_id,
                    entity_ids['survey_header_id'],
                    formation_inputs['surveyHeader']['stations']
                )
            
            # Update datum
            update_datum(self.root, payload.get('datum', {}), entity_ids)
            
            # Update casing schematics
            casing_schematics = payload.get('casingSchematics', {})
            if 'assemblies' in casing_schematics and well_id and wellbore_id:
                self.update_casing_assemblies(
                    well_id,
                    wellbore_id,
                    casing_schematics['assemblies']
                )
            
            logger.info("Template update from payload completed successfully")
        
            # Add binary data from template if requested
            if add_binary_data:
                logger.info("Adding binary data to the XML")
                inject_binary_data(self.root, self.template_path)
                    
            logger.info("Template update complete")
            return True

        except Exception as e:
            logger.error(f"Error updating from payload: {str(e)}", exc_info=True)
            return False
    
    def inject_binary_data(self) -> bool:
        """
        Inject binary data from binary_data_library.xml into the XML.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return inject_binary_data(self.root, self.template_path)