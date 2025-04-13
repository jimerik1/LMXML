
# XML Generator API

A service for generating EDM-compatible XML documents from JSON data based on templates.

## 🧾 Overview

This API generates properly formatted XML files for EDM software by converting structured JSON data, including:

- Well information
- Formation inputs
- Casing schematics

It handles ID generation, reference management, and XML formatting according to EDM requirements.

## ✨ Features

- **Standard Mode**: Generate complete XML files from scratch
- **Template Mode**: Update specific elements in existing XML templates while preserving IDs
- **ID Management**: Automatic generation and tracking of entity IDs
- **Reference Integrity**: Maintains proper relationships between XML elements

## ⚙️ Setup

### Prerequisites

- Python 3.9+
- Docker (recommended)

### 🐳 Docker Setup (Recommended)

```bash
# Build and run the container
docker compose up --build
```

The API will be available at `http://localhost:5055`.

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/xml/generate` | POST | Generate XML file |
| `/api/xml/download/<filename>` | GET | Download XML file |
| `/api/xml/validate` | POST | Validate payload |
| `/api/xml/template-info` | GET | Get template information |
| `/api/xml/schema` | GET | Get schema information |
| `/api/xml/template-mode-info` | GET | Get template mode information |

### Generate XML File (`/api/xml/generate`)

**Query Parameters**:
- `download` (boolean): Return file directly instead of file info
- `template_mode` (boolean): Use template mode
- `template_path` (string, optional): Custom template path

## 🧪 Example Usage

### 📤 Using `curl`

```bash
# Generate XML in standard mode
curl -X POST -H "Content-Type: application/json" -d @example_payload.json http://localhost:5055/api/xml/generate

# Generate XML in template mode
curl -X POST -H "Content-Type: application/json" -d @template_update_payload.json http://localhost:5055/api/xml/generate?template_mode=true

# Validate payload
curl -X POST -H "Content-Type: application/json" -d @example_payload.json http://localhost:5055/api/xml/validate

# Download generated file
curl -O http://localhost:5055/api/xml/download/<filename>
```

### 🐍 Using Python

```python
import requests
import json

# Load payload
with open('example_payload.json', 'r') as f:
    payload = json.load(f)

# Generate XML
response = requests.post('http://localhost:5055/api/xml/generate', json=payload)
result = response.json()

# Get the generated file
file_path = result['file_path']
download_url = f'http://localhost:5055/api/xml/download/{file_path}'
xml_content = requests.get(download_url).text

# Save the file
with open('generated_edm.xml', 'w') as f:
    f.write(xml_content)
```

## 🧩 Template Mode

Template mode allows updating specific elements in an existing XML file while preserving IDs. This is useful for making targeted changes without regenerating the entire structure.

**Supported Updates**:
- Site, well, wellbore, and scenario names
- Temperature profiles
- Pressure profiles
- DLS overrides
- Survey stations
- Datum information

## 📁 Working with Generated Files

Generated XML files are stored in the `output/` directory. When using Docker, this directory is mounted as a volume, making files accessible on the host machine.

## 📂 Project Structure

```
xml-generator-api/
├── README.md               # Project documentation
├── app.py                  # Main application
├── config.py               # Configuration settings
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Project dependencies
├── controllers/            # API route handlers
├── models/                 # Data models
├── services/               # Business logic services
│   ├── id_registry.py      # ID generation and tracking
│   └── xml_generator.py    # Main XML generation service
├── templates/              # Base XML templates
├── utils/                  # Utility functions
└── output/                 # Generated XML files directory
```
