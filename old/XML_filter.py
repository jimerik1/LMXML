import xml.etree.ElementTree as ET
import re

def process_xml(input_file, output_file):
    # Read the entire file as text first
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the XML declaration and processing instruction
    xml_declaration = '<?xml version="1.0" standalone="no"?>'
    data_services_match = re.search(r'<\?DataServices.*?\?>', content, re.DOTALL)
    data_services = data_services_match.group(0) if data_services_match else ''
    
    # Parse the XML
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Define the elements to keep
    needed_elements = [
        'TOPLEVEL',
        'MD_SITE_TIGHT_GROUP',
        'CD_SITE',
        'CD_WELL',
        'CD_WELLBORE',
        'CD_SCENARIO',
        'TU_DLS_OVERRIDE_GROUP',
        'TU_DLS_OVERRIDE',
        'TU_ZONE_PRESSURE_GROUP',
        'TU_ZONE_PRESSURE',
        'CD_ASSEMBLY',
        'CD_ASSEMBLY_COMP',
        'CD_WEQP_PACKER',
        'CD_CASE',
        'CD_CASE_TEMP_GRADIENT',
        'TU_CASE_ASSEMBLY_PARAMETER',
        'CD_TEMP_GRADIENT_GROUP',
        'CD_TEMP_GRADIENT',
        'CD_PORE_PRESSURE_GROUP',
        'CD_PORE_PRESSURE',
        'CD_FRAC_GRADIENT_GROUP',
        'CD_FRAC_GRADIENT',
        'CD_DEFINITIVE_SURVEY_HEADER',
        'CD_DEFINITIVE_SURVEY_STATION',
        'CD_DATUM'
    ]
    
    # Create a new root element
    new_root = ET.Element('export')
    
    # Process each child of the original root
    for child in root:
        tag = child.tag
        if tag in needed_elements:
            # Add this element to the new root
            new_root.append(child)
    
    # Create a new tree with the filtered elements
    new_tree = ET.ElementTree(new_root)
    
    # Write to a temporary file (ElementTree will add its own XML declaration)
    temp_file = output_file + '.temp'
    new_tree.write(temp_file, encoding='utf-8', xml_declaration=False)
    
    # Read the temporary file
    with open(temp_file, 'r', encoding='utf-8') as f:
        filtered_content = f.read()
    
    # Combine everything and write to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_declaration + '\n')
        f.write(data_services + '\n\n')
        f.write(filtered_content)
    
    # Clean up the temporary file
    import os
    os.remove(temp_file)

if __name__ == "__main__":
    input_file = "base.xml"  # Replace with your actual input file
    output_file = "filtered_output2.xml"  # Output file name
    process_xml(input_file, output_file)
    print(f"Filtered XML has been saved to {output_file}")