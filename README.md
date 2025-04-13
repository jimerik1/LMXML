# XML Generator API

A service for generating EDM-compatible XML documents based on templates.

## Overview

This API allows you to generate XML files for use with EDM software by providing structured JSON data describing well information, formation data, and casing schematics. The service handles ID generation, reference management, and proper XML formatting according to EDM requirements.
The API now supports two modes:

Standard mode: Generates a complete XML file from scratch
Template mode: Updates specific elements in an existing XML template while preserving IDs


## Project Structure

```
└── xml-generator-api/
    ├── README.md
    ├── app.py                # Main application entry point
    ├── config.py             # Configuration settings
    ├── Dockerfile            # Docker configuration
    ├── docker-compose.yml    # Docker Compose configuration
    ├── requirements.txt      # Project dependencies
    ├── controllers/          # API route handlers
    │   ├── __init__.py
    │   └── xml_controller.py
    ├── models/               # Data models
    │   ├── __init__.py
    │   └── schemas.py
    ├── services/             # Business logic services
    │   ├── __init__.py
    │   ├── id_registry.py    # ID generation and tracking
    │   └── xml_generator.py  # Main XML generation service
    ├── templates/            # Directory for base XML templates
    │   └── base_template.xml # Base template for XML generation
    ├── utils/                # Utility functions
    │   ├── __init__.py
    │   ├── validators.py
    │   └── xml_helpers.py    # XML manipulation helpers
    └── output/               # Generated XML files directory
```

## Setup

### Prerequisites

- Python 3.9+
- Flask
- Docker (optional)

### Standard Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

### Docker Setup (Recommended)

1. Make sure Docker and Docker Compose are installed
2. Build and run the container:
   ```bash
   docker compose up --build
   ```
3. The API will be available at http://localhost:5000

## API Endpoints

### Health Check

```
GET /health
```

Simple endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### Generate XML File

```
POST /api/xml/generate
```

Generate an XML file from a JSON payload.

**Query Parameters:**
- `download` (boolean): If true, returns the file directly instead of file information

**Request Body:** JSON payload (see example below)

**Response (when download=false):**
```json
{
  "status": "success",
  "message": "XML file generated successfully",
  "file_path": "tmpnpvzo7xh.xml",
  "file_name": "NSP-A-24X.xml"
}
```

### Download XML File

```
GET /api/xml/download/<filename>
```

Download a previously generated XML file.

**Parameters:**
- `filename`: Name of the file to download (e.g., from file_path in generate response)

**Response:** XML file download

### Validate Payload

```
POST /api/xml/validate
```

Validate a JSON payload without generating an XML file.

**Request Body:** JSON payload (same format as /generate)

**Response (success):**
```json
{
  "status": "success",
  "message": "Payload is valid",
  "validation": true
}
```

**Response (failure):**
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "projectInfo.well.isOffshore": ["Not a valid value."]
  },
  "validation": false
}
```

### Template Mode
The API now supports a template mode that allows you to update specific elements in an existing XML file without regenerating all IDs. This mode is useful when you want to make targeted changes to an XML file while preserving the overall structure and IDs.

### Using Template Mode

To use template mode, add the template_mode=true query parameter to the /api/xml/generate endpoint. You can also specify a custom template file using the template_path parameter.

```
POST /api/xml/generate?template_mode=true
Content-Type: application/json

{
  "projectInfo": {
    "site": {
      "siteName": "Updated Site Name"
    },
    "well": {
      "wellCommonName": "Updated Well Name"
    },
    "wellbore": {
      "wellboreName": "Updated Wellbore Name"
    }
  },
  "formationInputs": {
    "temperatureProfiles": [
      {"depth": 0, "temperature": 60, "units": "F"},
      {"depth": 5000, "temperature": 155, "units": "F"}
    ],
    "dlsOverrideGroup": {
      "overrides": [
        {"topDepth": 1000, "baseDepth": 1500, "doglegSeverity": 3.5},
        {"topDepth": 2000, "baseDepth": 2500, "doglegSeverity": 2.5}
      ]
    }
  },
  "datum": {
    "datumName": "Updated Datum",
    "datumElevation": 32.5
  }
} 


### Get Template Information

```
GET /api/xml/template-info
```

Get information about the XML template structure.

**Response:** JSON representation of template elements and attributes

### Get Schema Information

```
GET /api/xml/schema
```

Get the JSON schema used for validating input payloads.

**Response:** JSON representation of validation schema

## Example Payload

```json
{
  "projectInfo": {
    "site": {
      "siteName": "North Sea Platform Alpha",
      "locCountry": "Netherlands",
      "geoLatitude": 52.6391,
      "geoLongitude": 6.6063
    },
    "well": {
      "wellCommonName": "NSP-A-24X",
      "isOffshore": "Y",
      "wellheadDepth": 28.15,
      "waterDepth": 45.2
    },
    "wellbore": {
      "wellboreName": "NSP-A-24X Main Bore",
      "wellboreType": "Production",
      "isActive": "Y"
    }
  },
  "formationInputs": {
    "temperatureProfiles": [
      {"depth": 0, "temperature": 59, "units": "F"},
      {"depth": 5000, "temperature": 150, "units": "F"}
    ],
    "pressureProfiles": [
      {
        "depth": 3000,
        "pressure": 2000,
        "pressureType": "Pore",
        "units": "psi"
      }
    ]
  },
  "casingSchematics": {
    "materials": [
      {
        "materialName": "L80-10%wear",
        "grade": "L80",
        "density": 490.0,
        "youngsModulus": 3.0E7,
        "poissonsRatio": 0.3,
        "thermalExpansionCoef": 6.9,
        "minYieldStress": 80000.0,
        "ultimateTensileStrength": 95000.0
      }
    ],
    "assemblies": [
      {
        "assemblyName": "9 5/8\" Surface Casing",
        "stringType": "Casing",
        "stringClass": "Surface",
        "assemblySize": 9.625,
        "holeSize": 12.25,
        "topDepth": 0.0,
        "baseDepth": 1642.06,
        "components": [
          {
            "componentType": "CASING",
            "outerDiameter": 9.625,
            "innerDiameter": 8.535,
            "length": 1313.98,
            "topDepth": 0.0,
            "bottomDepth": 1313.98,
            "connectionType": "4",
            "weight": 53.5
          }
        ]
      }
    ]
  },
  "datum": {
    "datumName": "RKB",
    "datumElevation": 31.17
  }
}
```

## Working with Generated Files

The generated XML files are stored in the `output` directory. When using Docker, this directory is mounted as a volume, so files are accessible on the host machine at `./output/` relative to the project root.

For example, if the API returns `"file_path": "tmpnpvzo7xh.xml"`, you can find the file at `./output/tmpnpvzo7xh.xml`.


## Example Usage

### Using curl

```bash
# Generate XML
curl -X POST -H "Content-Type: application/json" -d @example_payload.json http://localhost:5000/api/xml/generate

# Validate payload
curl -X POST -H "Content-Type: application/json" -d @example_payload.json http://localhost:5000/api/xml/validate

# Download generated file
curl -O http://localhost:5000/api/xml/download/tmpnpvzo7xh.xml
```

### Using Python requests

```python
import requests
import json

# Load example payload
with open('example_payload.json', 'r') as f:
    payload = json.load(f)

# Generate XML
response = requests.post('http://localhost:5000/api/xml/generate', json=payload)
result = response.json()

# Get the generated file
file_path = result['file_path']
download_url = f'http://localhost:5000/api/xml/download/{file_path}'
xml_content = requests.get(download_url).text

# Save the file
with open('generated_edm.xml', 'w') as f:
    f.write(xml_content)
```