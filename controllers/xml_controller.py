# controllers/xml_controller.py
import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from marshmallow import ValidationError

from config import active_config
from models.schemas import PayloadSchema
from services.xml_template_editor import XMLTemplateEditor

# Create a blueprint for XML routes
xml_bp = Blueprint('xml', __name__)

@xml_bp.route('/generate', methods=['POST'])
def generate_xml():
    """
    Generate an XML file from a JSON payload using template mode.
    
    The endpoint accepts a JSON payload and updates an existing XML template
    while preserving IDs and relationships.
    
    Request Parameters:
        download (bool): Whether to return the file directly (default: false)
        template_path (str): Path to the template file (optional)
        add_binary_data (bool): Whether to add binary data (default: false)
    
    Returns:
        JSON response with status and file info, or the file directly
    """
    try:
        # Log request information
        print(f"Received request to /generate with params: {request.args}")
        
        # Validate the request payload
        schema = PayloadSchema()
        payload = schema.load(request.json)
        print(f"Payload validation successful")
        
        # Check if binary data should be added
        add_binary_data = request.args.get('add_binary_data', 'false').lower() == 'true'
        print(f"Add binary data: {add_binary_data}")
        
        # Use the template editor to update an existing XML file
        template_path = request.args.get('template_path')
        
        if not template_path:
            # Use the default template
            template_path = os.path.join(active_config.TEMPLATE_DIR, 'edm_template.xml')
            print(f"Using default template path: {template_path}")
        
        if not os.path.exists(template_path):
            print(f"Template file not found: {template_path}")
            return jsonify({
                'status': 'error',
                'message': f'Template file not found: {template_path}'
            }), 404
        
        print(f"Creating template editor with template: {template_path}")
        # Create template editor and update the XML
        editor = XMLTemplateEditor(template_path)
        
        print("Updating template from payload")
        if not editor.update_from_payload(payload, add_binary_data):
            print("Failed to update XML template")
            return jsonify({
                'status': 'error',
                'message': 'Failed to update XML template'
            }), 500
        
        # Get the updated XML
        print("Getting updated XML string")
        xml_content = editor.get_xml_string()
        
        # Save to a temporary file
        print("Saving to temporary file")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.edm.xml', dir=active_config.OUTPUT_DIR) as temp:
            temp.write(xml_content.encode('utf-8'))
            temp_path = temp.name
        
        # Get a file name based on the well name if available
        well_name = payload.get('projectInfo', {}).get('well', {}).get('wellCommonName', 'output')
        file_name = f"{well_name.replace(' ', '_')}.edm.xml"
        
        print(f"Generated file: {temp_path}, filename: {file_name}")
        
        # Return the file or a download link
        if request.args.get('download', 'false').lower() == 'true':
            print("Returning file for download")
            return send_file(
                temp_path,
                as_attachment=True,
                attachment_filename=file_name,
                mimetype='application/xml'
            )
        else:
            print("Returning file info")
            return jsonify({
                'status': 'success',
                'message': 'XML file generated successfully',
                'file_path': os.path.basename(temp_path),
                'file_name': file_name
            })
            
    except ValidationError as e:
        print(f"Validation error: {e.messages}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        print(f"Error generating XML: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500