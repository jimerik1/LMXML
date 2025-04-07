# XML generation service
from lxml import etree as ET
from services.id_registry import IDRegistry
from utils.xml_helpers import (
    load_xml_template, 
    convert_camel_to_xml_key,
    find_element_by_attributes,
    create_or_update_element,
    xml_to_string
)

class XMLGenerator:
    """Service for generating XML files from structured data."""
    
    def __init__(self, base_template_path):
        self.base_template_path = base_template_path
        self.id_registry = IDRegistry()
    
    def generate_xml(self, payload):
        """Generate XML from a structured payload."""
        # Load the template
        tree = load_xml_template(self.base_template_path)
        root = tree.getroot()
        
        # Generate and register IDs as needed
        self._prepare_ids(payload)
        
        # Update the XML structure
        self._update_project_info(root, payload.get('projectInfo', {}))
        self._update_formation_inputs(root, payload.get('formationInputs', {}))
        self._update_casing_schematics(root, payload.get('casingSchematics', {}))
        
        # Validate relationships
        validation_errors = self.id_registry.validate_references()
        if validation_errors:
            raise ValueError("\n".join(validation_errors))
        
        # Return the XML as a string
        return xml_to_string(root)
    
    def _prepare_ids(self, payload):
        """Generate and register IDs for entities in the payload."""
        # This would process the payload and establish all required IDs
        # Implementation depends on specific ID requirements
        pass
    
    def _update_project_info(self, root, project_info):
        """Update project information in the XML."""
        if not project_info:
            return
            
        # Update site information
        if 'site' in project_info:
            site_elem = root.find(".//CD_SITE")
            if site_elem is None:
                # Create element if it doesn't exist
                site_elem = ET.SubElement(root.find(".//export"), "CD_SITE")
            
            # Update attributes
            for key, value in project_info['site'].items():
                xml_key = convert_camel_to_xml_key(key)
                site_elem.set(xml_key, str(value))
        
        # Similar implementation for well, wellbore, and scenario
        # ...
    
    def _update_formation_inputs(self, root, formation_inputs):
        """Update formation inputs in the XML."""
        # Implementation for temperature, pressure, etc.
        pass
    
    def _update_casing_schematics(self, root, casing_schematics):
        """Update casing schematics in the XML."""
        # Implementation for assemblies and components
        pass