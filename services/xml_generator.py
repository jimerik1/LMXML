# services/xml_generator.py
from lxml import etree as ET
import os
from services.id_registry import IDRegistry
from utils.xml_helpers import (
    load_xml_template, 
    xml_to_string,
    fix_xml_structure
)

# Import method implementations
from services.xml_methods.core import initialize, generate_xml
from services.xml_methods.clear import clear_template_elements
from services.xml_methods.ids import prepare_ids, get_parent_id
from services.xml_methods.project_info import update_project_info
from services.xml_methods.formation import update_formation_inputs
from services.xml_methods.dls import update_dls_overrides
from services.xml_methods.survey import update_survey_header
from services.xml_methods.casing import update_casing_schematics
from services.xml_methods.datum import update_datum
from services.xml_methods.scenario import add_scenario_element, add_case_elements
from services.xml_methods.binary import inject_binary_data, update_locator_id
from services.xml_methods.utils import add_creation_info

class XMLGenerator:
    """
    Service for generating XML files from structured data.
    
    This generator preserves the structure of a base template while
    updating specific elements based on the provided payload.
    """
    
    def __init__(self, base_template_path):
        """Initialize the XML generator with a template path."""
        initialize(self, base_template_path)
    
    def generate_xml(self, payload):
        """Generate XML from a structured payload by updating the template."""
        return generate_xml(self, payload)
    
    def _clear_template_elements(self, export_elem, payload):
        """Clear elements from the template that will be replaced by payload data."""
        clear_template_elements(self, export_elem, payload)
    
    def _prepare_ids(self, payload):
        """Generate and register IDs for entities in the payload."""
        prepare_ids(self, payload)
    
    def _update_project_info(self, export_elem, project_info):
        """Update project information in the XML."""
        update_project_info(self, export_elem, project_info)
    
    def _update_formation_inputs(self, export_elem, formation_inputs):
        """Update formation inputs in the XML."""
        update_formation_inputs(self, export_elem, formation_inputs)
    
    def _update_dls_overrides(self, export_elem, dls_override_group):
        """Update dogleg severity overrides in the XML."""
        update_dls_overrides(self, export_elem, dls_override_group)
    
    def _update_survey_header(self, export_elem, survey_header):
        """Update survey header and stations in the XML."""
        update_survey_header(self, export_elem, survey_header)
    
    def _update_casing_schematics(self, export_elem, casing_schematics):
        """Update casing schematics in the XML."""
        update_casing_schematics(self, export_elem, casing_schematics)
    
    def _update_datum(self, export_elem, datum):
        """Update datum information in the XML."""
        update_datum(self, export_elem, datum)
    
    def _add_scenario_element(self, export_elem):
        """Add scenario element to link different components together."""
        add_scenario_element(self, export_elem)
    
    def _add_case_elements(self, export_elem):
        """Add case elements to link scenarios to assemblies."""
        add_case_elements(self, export_elem)
    
    def _inject_binary_data(self, export_elem):
        """Inject binary data from binary_data_library.xml into the export element."""
        inject_binary_data(self, export_elem)
    
    def _update_locator_id(self, locator, id_prefix, new_id):
        """Update an ID in an attachment locator string."""
        return update_locator_id(self, locator, id_prefix, new_id)
    
    def _add_creation_info(self, elem):
        """Add creation and update info to an element."""
        add_creation_info(self, elem)
    
    def _get_parent_id(self, parent_type, child_type, child_id):
        """Find parent ID based on relationship."""
        return get_parent_id(self, parent_type, child_type, child_id)