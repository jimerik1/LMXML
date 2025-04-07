import os
import sys

def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path, content=""):
    """Create a file with optional content."""
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")

def create_xml_generator_structure():
    """Create the XML generator API directory structure."""
    base_dir = "xml-generator-api"
    create_directory(base_dir)
    
    # Create main application files
    create_file(os.path.join(base_dir, "app.py"), "# Main application entry point\n")
    create_file(os.path.join(base_dir, "config.py"), "# Configuration settings\n")
    create_file(os.path.join(base_dir, "requirements.txt"), "# Project dependencies\n")
    
    # Create README
    readme_content = """# XML Generator API

A service for generating XML documents based on templates.

## Project Structure
- `app.py`: Main application entry point
- `config.py`: Configuration settings
- `templates/`: Directory for base XML templates
- `services/`: Business logic services
- `utils/`: Utility functions
- `models/`: Data models
- `controllers/`: API route handlers
"""
    create_file(os.path.join(base_dir, "README.md"), readme_content)
    
    # Create templates directory and files
    templates_dir = os.path.join(base_dir, "templates")
    create_directory(templates_dir)
    base_template_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <!-- Base XML template -->
</root>
"""
    create_file(os.path.join(templates_dir, "base_template.xml"), base_template_content)
    
    # Create services directory and files
    services_dir = os.path.join(base_dir, "services")
    create_directory(services_dir)
    create_file(os.path.join(services_dir, "__init__.py"), "# Services package initialization\n")
    create_file(os.path.join(services_dir, "xml_generator.py"), "# XML generation service\n")
    create_file(os.path.join(services_dir, "id_registry.py"), "# ID management service\n")
    
    # Create utils directory and files
    utils_dir = os.path.join(base_dir, "utils")
    create_directory(utils_dir)
    create_file(os.path.join(utils_dir, "__init__.py"), "# Utils package initialization\n")
    create_file(os.path.join(utils_dir, "xml_helpers.py"), "# XML manipulation utilities\n")
    create_file(os.path.join(utils_dir, "validators.py"), "# Input validation\n")
    
    # Create models directory and files
    models_dir = os.path.join(base_dir, "models")
    create_directory(models_dir)
    create_file(os.path.join(models_dir, "__init__.py"), "# Models package initialization\n")
    create_file(os.path.join(models_dir, "schemas.py"), "# JSON validation schemas\n")
    
    # Create controllers directory and files
    controllers_dir = os.path.join(base_dir, "controllers")
    create_directory(controllers_dir)
    create_file(os.path.join(controllers_dir, "__init__.py"), "# Controllers package initialization\n")
    create_file(os.path.join(controllers_dir, "xml_controller.py"), "# API endpoint controllers\n")
    
    print("\nXML Generator API directory structure created successfully!")

if __name__ == "__main__":
    create_xml_generator_structure()