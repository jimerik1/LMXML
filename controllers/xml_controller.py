# controllers/xml_controller.py
import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from marshmallow import ValidationError

from config import active_config
from models.schemas import PayloadSchema
from services.xml_generator import XMLGenerator

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