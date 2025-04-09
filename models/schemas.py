# models/schemas.py
from marshmallow import Schema, fields, validate

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
    assemblyId = fields.String()
    componentType = fields.String(required=True)
    materialId = fields.String()
    outerDiameter = fields.Float(required=True)
    innerDiameter = fields.Float(required=True)
    length = fields.Float(required=True)
    topDepth = fields.Float(required=True)
    bottomDepth = fields.Float(required=True)
    connectionType = fields.String()
    weight = fields.Float()
    pressureBurst = fields.Float()
    pressureCollapse = fields.Float()
    axialStrength = fields.Float()

class CasingAssemblySchema(Schema):
    """Validation schema for casing assemblies."""
    assemblyId = fields.String()
    wellboreId = fields.String()
    assemblyName = fields.String(required=True)
    stringType = fields.String(required=True)
    stringClass = fields.String()
    assemblySize = fields.Float()
    holeSize = fields.Float()
    topDepth = fields.Float(required=True)
    baseDepth = fields.Float(required=True)
    components = fields.List(fields.Nested(CasingComponentSchema))

class ProjectInfoSchema(Schema):
    """Validation schema for project information."""
    site = fields.Nested(SiteSchema)
    well = fields.Nested(WellSchema)
    wellbore = fields.Nested(WellboreSchema)

class FormationInputsSchema(Schema):
    """Validation schema for formation inputs."""
    temperatureProfiles = fields.List(fields.Nested(TemperatureProfileSchema))
    pressureProfiles = fields.List(fields.Nested(PressureProfileSchema))

class CasingSchematifsSchema(Schema):
    """Validation schema for casing schematics."""
    materials = fields.List(fields.Nested(MaterialPropertySchema))
    assemblies = fields.List(fields.Nested(CasingAssemblySchema))

class PayloadSchema(Schema):
    """Main validation schema for API payload."""
    projectInfo = fields.Nested(ProjectInfoSchema, required=True)
    formationInputs = fields.Nested(FormationInputsSchema)
    casingSchematics = fields.Nested(CasingSchematifsSchema)