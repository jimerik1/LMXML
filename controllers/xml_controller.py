# controllers/xml_controller.py
import os
import tempfile
import logging
from flask import Blueprint, request, jsonify, send_file
from marshmallow import ValidationError
from typing import Dict, Any, Tuple

from config import active_config
from models.schemas import PayloadSchema
from services.xml_template_editor import XMLTemplateEditor

# Configure logging
logger = logging.getLogger(__name__)

# Create a blueprint for XML routes
xml_bp = Blueprint('xml', __name__)

@xml_bp.route('/generate', methods=['POST'])
def generate_xml() -> Tuple[Any, int]:
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
        logger.info(f"Received request to /generate with params: {request.args}")
        
        # Validate the request payload
        schema = PayloadSchema()
        payload = schema.load(request.json)
        logger.info(f"Payload validation successful")
        
        # Process query parameters
        params = _get_request_parameters()
        
        # Get template path
        template_path = _get_template_path(params.get('template_path'))
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            return jsonify({
                'status': 'error',
                'message': f'Template file not found: {template_path}'
            }), 404
        
        # Create and update XML template
        return _process_xml_template(template_path, payload, params)
            
    except ValidationError as e:
        logger.error(f"Validation error: {e.messages}")
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except Exception as e:
        logger.error(f"Error generating XML: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def _get_request_parameters() -> Dict[str, Any]:
    """Extract and process request parameters."""
    return {
        'download': request.args.get('download', 'false').lower() == 'true',
        'template_path': request.args.get('template_path'),
        'add_binary_data': request.args.get('add_binary_data', 'false').lower() == 'true'
    }

def _get_template_path(custom_template_path: str = None) -> str:
    """Get the template path, using default if not provided."""
    if custom_template_path:
        logger.info(f"Using custom template path: {custom_template_path}")
        return custom_template_path
    
    # Use the default template
    template_path = os.path.join(active_config.TEMPLATE_DIR, 'edm_template.xml')
    logger.info(f"Using default template path: {template_path}")
    return template_path

def _process_xml_template(template_path: str, payload: Dict[str, Any], 
                          params: Dict[str, Any]) -> Tuple[Any, int]:
    """Process the XML template with the given payload and parameters."""
    # Create template editor 
    logger.info(f"Creating template editor with template: {template_path}")
    editor = XMLTemplateEditor(template_path)
    
    # Update the XML from payload
    logger.info("Updating template from payload")
    if not editor.update_from_payload(payload, params.get('add_binary_data', False)):
        logger.error("Failed to update XML template")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update XML template'
        }), 500
    
    # Get the updated XML and save to file
    logger.info("Getting updated XML string")
    xml_content = editor.get_xml_string()
    
    # Save to temporary file
    logger.info("Saving to temporary file")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.edm.xml', 
                                     dir=active_config.OUTPUT_DIR) as temp:
        temp.write(xml_content.encode('utf-8'))
        temp_path = temp.name
    
    # Get a file name based on the well name if available
    well_name = payload.get('projectInfo', {}).get('well', {}).get('wellCommonName', 'output')
    file_name = f"{well_name.replace(' ', '_')}.edm.xml"
    
    logger.info(f"Generated file: {temp_path}, filename: {file_name}")
    
    # Return the file or a download link
    if params.get('download', False):
        logger.info("Returning file for download")
        return send_file(
            temp_path,
            as_attachment=True,
            attachment_filename=file_name,
            mimetype='application/xml'
        )
    else:
        logger.info("Returning file info")
        return jsonify({
            'status': 'success',
            'message': 'XML file generated successfully',
            'file_path': os.path.basename(temp_path),
            'file_name': file_name
        })