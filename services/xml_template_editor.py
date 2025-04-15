# services/xml_template_editor.py
"""
Wrapper module for backward compatibility.
This file imports from the new modular structure to maintain 
compatibility with existing code.
"""

import logging
from services.xml.template_editor import XMLTemplateEditor

# Configure logging
logger = logging.getLogger(__name__)

# Export the main class
__all__ = ['XMLTemplateEditor']