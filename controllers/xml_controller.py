# API endpoint controllers
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
    """Generate an XML file from a JSON payload."""
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
        
        # Return the file or a download link
        if request.args.get('download', 'false').lower() == 'true':
            return send_file(
                temp_path,
                as_attachment=True,
                attachment_filename=f"{payload.get('projectInfo', {}).get('well', {}).get('wellCommonName', 'output')}.xml",
                mimetype='application/xml'
            )
        else:
            return jsonify({
                'status': 'success',
                'message': 'XML file generated successfully',
                'file_path': os.path.basename(temp_path)
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
    """Download a previously generated XML file."""
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