# models/schemas.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from typing import Dict, Any

class SiteSchema(Schema):
    """Validation schema for site information."""
    siteId = fields.String()
    projectId = fields.String()
    siteName = fields.String(required=True)
    locCountry = fields.String()
    geoLatitude = fields.Float()
    geoLongitude = fields.Float()

class WellSchema(Schema):
    """Validation schema for well information."""
    wellId = fields.String()
    siteId = fields.String()
    isOffshore = fields.String(validate=validate.OneOf(['Y', 'N']))
    wellCommonName = fields.String(required=True)
    wellheadDepth = fields.Float()
    waterDepth = fields.Float()

class WellboreSchema(Schema):
    """Validation schema for wellbore information."""
    wellboreId = fields.String()
    wellId = fields.String()
    wellboreName = fields.String(required=True)
    wellboreType = fields.String()
    isActive = fields.String(validate=validate.OneOf(['Y', 'N']))

class TemperatureProfileSchema(Schema):
    """Validation schema for temperature profile."""
    depth = fields.Float(required=True)
    temperature = fields.Float(required=True)
    units = fields.String(validate=validate.OneOf(['F', 'C']))

class PressureProfileSchema(Schema):
    """Validation schema for pressure profiles."""
    depth = fields.Float(required=True)
    pressure = fields.Float(required=True)
    pressureType = fields.String(validate=validate.OneOf(['Pore', 'Frac', 'Hydrostatic']))
    units = fields.String(validate=validate.OneOf(['psi', 'bar', 'kPa']))
    
    @validates_schema
    def validate_pressure_type(self, data: Dict[str, Any], **kwargs) -> None:
        """Validate that pressureType is provided."""
        if 'pressureType' not in data:
            raise ValidationError("pressureType is required")

class MaterialPropertySchema(Schema):
    """Validation schema for material properties."""
    materialId = fields.String()
    materialName = fields.String(required=True)
    grade = fields.String()
    density = fields.Float()
    youngsModulus = fields.Float()
    poissonsRatio = fields.Float()
    thermalExpansionCoef = fields.Float()
    minYieldStress = fields.Float()
    ultimateTensileStrength = fields.Float()

class CasingComponentSchema(Schema):
    """Validation schema for casing components."""
    componentId = fields.String()
    componentType = fields.String(required=True)  # CAS, TBG, PKR, etc.
    materialId = fields.String()
    outerDiameter = fields.Float()  # Not required for all component types
    innerDiameter = fields.Float()  # Not required for all component types
    length = fields.Float()         # Not required for all component types
    topDepth = fields.Float(required=True)  
    bottomDepth = fields.Float(required=True)
    connectionType = fields.String()
    connectionName = fields.String()  # Added this field
    connectionGrade = fields.String()
    weight = fields.Float()  # APPROXIMATE_WEIGHT
    grade = fields.String()
    pressureBurst = fields.Float()
    pressureCollapse = fields.Float()
    axialStrength = fields.Float()  # AXIAL_RATING
    
    # Additional packer-specific fields
    packerName = fields.String()
    packerDepth = fields.Float()
    plugDepth = fields.Float()
    
    # Additional fields
    jointStrength = fields.Float()
    pipeType = fields.String()
    poissonsRatio = fields.Float()
    minYieldStress = fields.Float()
    ultimateTensileStrength = fields.Float()
    thermalExpansionCoef = fields.Float()
    youngsModulus = fields.Float()
    wallThicknessPercent = fields.Float()
    
    @validates_schema
    def validate_component_type(self, data: Dict[str, Any], **kwargs) -> None:
        """
        Validate that required fields are present based on component type.
        """
        if data.get('componentType') in ['CAS', 'TBG']:
            required_fields = ['outerDiameter', 'innerDiameter', 'length']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValidationError(f"{field} is required for component type {data.get('componentType')}")

class CasingAssemblySchema(Schema):
    """Validation schema for casing assemblies."""
    assemblyId = fields.String()
    wellboreId = fields.String()
    assemblyName = fields.String(required=True)
    stringType = fields.String(required=True)  # Liner, Casing, Tubing, etc.
    stringClass = fields.String()  # Production, Surface, etc.
    assemblySize = fields.Float(required=True)
    holeSize = fields.Float(required=True)
    topDepth = fields.Float(required=True)  # MD_ASSEMBLY_TOP
    baseDepth = fields.Float(required=True)  # MD_ASSEMBLY_BASE
    tocDepth = fields.Float()  # MD_TOC (Top of Cement)
    mudDensityShoe = fields.Float()
    isTopDown = fields.String(validate=validate.OneOf(['Y', 'N']), default='Y')
    components = fields.List(fields.Nested(CasingComponentSchema))

class DLSOverrideSchema(Schema):
    """Validation schema for dogleg severity overrides."""
    overrideId = fields.String()
    topDepth = fields.Float(required=True)
    baseDepth = fields.Float(required=True)
    doglegSeverity = fields.Float(required=True)

class DLSOverrideGroupSchema(Schema):
    """Validation schema for dogleg severity override groups."""
    groupId = fields.String()
    scenarioId = fields.String()
    wellboreId = fields.String()
    overrides = fields.List(fields.Nested(DLSOverrideSchema), required=True)

class SurveyStationSchema(Schema):
    """Validation schema for definitive survey stations."""
    stationId = fields.String()
    azimuth = fields.Float(required=True)
    inclination = fields.Float(required=True)
    md = fields.Float(required=True)
    tvd = fields.Float()
    doglegSeverity = fields.Float()
    sequenceNo = fields.Integer()
    dataEntryMode = fields.Integer()

class SurveyHeaderSchema(Schema):
    """Validation schema for definitive survey headers."""
    headerId = fields.String()
    wellboreId = fields.String()
    name = fields.String(required=True)
    phase = fields.String()
    bhMd = fields.Float()
    interpolationInterval = fields.Float()
    stations = fields.List(fields.Nested(SurveyStationSchema))

class DatumSchema(Schema):
    """Validation schema for datum information."""
    datumId = fields.String()
    wellId = fields.String()
    datumName = fields.String(required=True)
    datumElevation = fields.Float(required=True)

class ProjectInfoSchema(Schema):
    """Validation schema for project information."""
    site = fields.Nested(SiteSchema)
    well = fields.Nested(WellSchema)
    wellbore = fields.Nested(WellboreSchema)

class FormationInputsSchema(Schema):
    """Validation schema for formation inputs."""
    temperatureProfiles = fields.List(fields.Nested(TemperatureProfileSchema))
    pressureProfiles = fields.List(fields.Nested(PressureProfileSchema))
    dlsOverrideGroup = fields.Nested(DLSOverrideGroupSchema)
    surveyHeader = fields.Nested(SurveyHeaderSchema)

class CasingSchematifsSchema(Schema):
    """Validation schema for casing schematics."""
    materials = fields.List(fields.Nested(MaterialPropertySchema))
    assemblies = fields.List(fields.Nested(CasingAssemblySchema))

class PayloadSchema(Schema):
    """Main validation schema for API payload."""
    projectInfo = fields.Nested(ProjectInfoSchema, required=True)
    formationInputs = fields.Nested(FormationInputsSchema)
    casingSchematics = fields.Nested(CasingSchematifsSchema)
    datum = fields.Nested(DatumSchema)