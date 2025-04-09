# controllers/xml_controller.py
import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from marshmallow import ValidationError

from config import active_config
from models.schemas import PayloadSchema
from services.xml_generator import XMLGenerator
from utils.xml_helpers import load_xml_template

# Create a blueprint for XML routes
xml_bp = Blueprint('xml', __name__)

# Initialize the XML generator with the base template
xml_generator = XMLGenerator(active_config.BASE_TEMPLATE_PATH)

@xml_bp.route('/generate', methods=['POST'])
def generate_xml():
    """
    Generate an XML file from a JSON payload.
    
    The endpoint accepts a JSON payload with well information, formation data,
    and casing schematics, then generates a properly formatted XML file 
    according to the specified format for external software.
    
    Request Parameters:
        download (bool): Whether to return the file directly (default: false)
    
    Returns:
        JSON response with status and file info, or the file directly
    """
    try:
        # Validate the request payload
        schema = PayloadSchema()
        payload = schema.load(request.json)
        
        # Generate the XML
        xml_content = xml_generator.generate_xml(payload)
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', dir=active_config.OUTPUT_DIR) as temp:
            temp.write(xml_content.encode('utf-8'))
            temp_path = temp.name
        
        # Get a file name based on the well name if available
        well_name = payload.get('projectInfo', {}).get('well', {}).get('wellCommonName', 'output')
        file_name = f"{well_name.replace(' ', '_')}.xml"
        
        # Return the file or a download link
        if request.args.get('download', 'false').lower() == 'true':
            return send_file(
                temp_path,
                as_attachment=True,
                attachment_filename=file_name,
                mimetype='application/xml'
            )
        else:
            return jsonify({
                'status': 'success',
                'message': 'XML file generated successfully',
                'file_path': os.path.basename(temp_path),
                'file_name': file_name
            })
            
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@xml_bp.route('/download/<filename>', methods=['GET'])
def download_xml(filename):
    """
    Download a previously generated XML file.
    
    Args:
        filename (str): Name of the file to download
        
    Returns:
        File download response or error message
    """
    file_path = os.path.join(active_config.OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({
            'status': 'error',
            'message': 'File not found'
        }), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        attachment_filename=filename,
        mimetype='application/xml'
    )

@xml_bp.route('/validate', methods=['POST'])
def validate_payload():
    """
    Validate a JSON payload without generating an XML file.
    
    Validates the structure and data types of the input JSON against the schema
    without performing the full XML generation process.
    
    Returns:
        JSON response with validation results
    """
    try:
        schema = PayloadSchema()
        payload = schema.load(request.json)
        return jsonify({
            'status': 'success',
            'message': 'Payload is valid',
            'validation': True
        })
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.messages,
            'validation': False
        }), 400

@xml_bp.route('/template-info', methods=['GET'])
def get_template_info():
    """
    Get information about the XML template structure.
    
    Returns information about the elements and attributes in the base template,
    useful for understanding the expected structure of the generated XML.
    
    Returns:
        JSON response with template element information
    """
    try:
        tree = load_xml_template(active_config.BASE_TEMPLATE_PATH)
        root = tree.getroot()
        
        # Extract information about elements
        elements = {}
        for child in root.findall(".//export/*"):
            tag = child.tag
            if tag not in elements:
                elements[tag] = []
            
            attrs = {attr: value for attr, value in child.attrib.items()}
            if attrs not in elements[tag]:
                elements[tag].append(attrs)
        
        return jsonify({
            'status': 'success',
            'template_elements': elements
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@xml_bp.route('/schema', methods=['GET'])
def get_schema():
    """
    Get the JSON schema for API payload validation.
    
    Returns a schema description that can be used to understand the expected
    structure and requirements of the input payload.
    
    Returns:
        JSON response with schema information
    """
    try:
        schema = PayloadSchema()
        return jsonify({
            'status': 'success',
            'schema': schema.fields
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500