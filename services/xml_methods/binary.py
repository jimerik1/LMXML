# services/xml_methods/binary.py
import os
from lxml import etree as ET

def inject_binary_data(generator, export_elem):
    """
    Inject binary data from binary_data_library.xml into the export element.
    Update IDs to be consistent with the generated XML.
    
    Args:
        generator: The XMLGenerator instance
        export_elem (Element): Export XML element
    """
    try:
        # Check if binary data library file exists
        if not os.path.exists(generator.binary_data_path):
            print(f"Warning: Binary data library not found at {generator.binary_data_path}")
            return
        
        # Load binary data library
        from utils.xml_helpers import load_xml_template
        binary_tree = load_xml_template(generator.binary_data_path)
        binary_root = binary_tree.getroot()
        
        # Find the BINARY_DATA element
        binary_data_elem = binary_root if binary_root.tag == 'BINARY_DATA' else binary_root.find(".//BINARY_DATA")
        
        if binary_data_elem is not None:
            # Create a new BINARY_DATA element in the export element
            binary_elem = ET.SubElement(export_elem, "BINARY_DATA")
            
            # Copy attributes
            for key, value in binary_data_elem.attrib.items():
                binary_elem.set(key, value)
            
            # Get the existing IDs from our registry
            well_ids = generator.id_registry.id_map.get('WELL', [])
            wellbore_ids = generator.id_registry.id_map.get('WELLBORE', [])
            scenario_ids = generator.id_registry.id_map.get('SCENARIO', [])
            
            # Process each attachment journal
            for journal_elem in binary_data_elem.findall("./CD_ATTACHMENT_JOURNAL"):
                # Create a new journal element
                new_journal = ET.SubElement(binary_elem, "CD_ATTACHMENT_JOURNAL")
                
                # Generate new IDs for the attachments
                attachment_id = generator.id_registry.generate_id('ATTACHMENT')
                attachment_journal_id = generator.id_registry.generate_id('ATTACHMENT_JOURNAL')
                
                # Copy and update attributes
                for key, value in journal_elem.attrib.items():
                    if key == "attachment_id":
                        new_journal.set(key, attachment_id)
                    elif key == "attachment_journal_id":
                        new_journal.set(key, attachment_journal_id)
                    elif key == "attachment_locator":
                        # Update the locator with our generated IDs
                        locator = value
                        
                        # Keep policy_id consistent
                        if "policy_id=" in locator and "policy_id=(Pzrgw9f4JC)" in locator:
                            # Don't change this ID as it's referenced elsewhere
                            pass
                        
                        # Replace well_id if we have one
                        if well_ids and "well_id=" in locator:
                            locator = update_locator_id(generator, locator, "well_id=", well_ids[0])
                        
                        # Replace wellbore_id if we have one
                        if wellbore_ids and "wellbore_id=" in locator:
                            locator = update_locator_id(generator, locator, "wellbore_id=", wellbore_ids[0])
                        
                        # Replace scenario_id if we have one
                        if scenario_ids and "scenario_id=" in locator:
                            locator = update_locator_id(generator, locator, "scenario_id=", scenario_ids[0])
                        
                        new_journal.set(key, locator)
                    else:
                        new_journal.set(key, value)
                
                # Process the child CD_ATTACHMENT element
                for attachment_elem in journal_elem.findall("./CD_ATTACHMENT"):
                    new_attachment = ET.SubElement(new_journal, "CD_ATTACHMENT")
                    
                    # Copy and update attributes
                    for key, value in attachment_elem.attrib.items():
                        if key == "attachment_id":
                            new_attachment.set(key, attachment_id)
                        else:
                            new_attachment.set(key, value)
                    
                    # Copy the binary data content
                    if attachment_elem.text:
                        new_attachment.text = attachment_elem.text
                    
                    # Copy any children of the attachment (if any)
                    for child in attachment_elem:
                        new_attachment.append(ET.fromstring(ET.tostring(child)))
                
                # Copy other content and trailing text (the binary data)
                if journal_elem.text and journal_elem.text.strip():
                    new_journal.text = journal_elem.text
                
                # Copy the text after the attachment element (often binary data)
                if len(journal_elem) > 0 and journal_elem[-1].tail and journal_elem[-1].tail.strip():
                    new_journal[-1].tail = journal_elem[-1].tail
        else:
            print("Warning: No BINARY_DATA element found in binary data library")
    except Exception as e:
        print(f"Error injecting binary data: {str(e)}")

def update_locator_id(generator, locator, id_prefix, new_id):
    """
    Update an ID in an attachment locator string.
    
    Args:
        generator: The XMLGenerator instance
        locator (str): The original locator string
        id_prefix (str): The prefix identifying the ID to replace (e.g., "well_id=")
        new_id (str): The new ID to use
        
    Returns:
        str: Updated locator string
    """
    # Find the start and end position of the ID
    start_pos = locator.find(id_prefix) + len(id_prefix)
    if start_pos < len(id_prefix):  # Not found
        return locator
    
    # Find the opening and closing parentheses
    open_paren = locator.find("(", start_pos)
    close_paren = locator.find(")", open_paren + 1)
    
    if open_paren >= 0 and close_paren > open_paren:
        # Replace the ID between the parentheses
        return locator[:open_paren+1] + new_id + locator[close_paren:]
    
    return locator