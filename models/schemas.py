# JSON validation schemas
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

# Add more schemas for other components...

class ProjectInfoSchema(Schema):
    """Validation schema for project information."""
    site = fields.Nested(SiteSchema)
    well = fields.Nested(WellSchema)
    # Add wellbore and scenario schemas

class PayloadSchema(Schema):
    """Main validation schema for API payload."""
    projectInfo = fields.Nested(ProjectInfoSchema)
    formationInputs = fields.Dict()  # Define a proper schema for this
    casingSchematics = fields.Dict()  # Define a proper schema for this