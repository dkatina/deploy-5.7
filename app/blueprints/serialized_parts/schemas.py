from app.extensions import ma
from app.models import SerializedPart
from marshmallow import fields

class SerializedPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        include_fk = True

serialized_part_schema = SerializedPartSchema()
serialized_parts_schema = SerializedPartSchema(many=True)

class ResponseSerializedPartSchema(ma.SQLAlchemyAutoSchema):
    description = fields.Nested("PartDescriptionSchema")
    class Meta:
        model = SerializedPart

response_schema = ResponseSerializedPartSchema()
responses_schema = ResponseSerializedPartSchema(many=True)