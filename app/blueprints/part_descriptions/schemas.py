from app.extensions import ma
from app.models import PartDescription

class PartDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescription

part_description_schema = PartDescriptionSchema()
part_descriptions_schema = PartDescriptionSchema(many=True)
