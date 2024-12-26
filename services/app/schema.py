from app.extensions import ma  # Імпорт Marshmallow з вашого розширення
from app.models import Service  # Імпорт вашої моделі Service

class ServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service
        load_instance = True
        include_relationships = True
        include_fk = True  # Додає поля зовнішніх ключів, таких як `depends_on_id`

    dependencies = ma.Nested(lambda: ServiceSchema(only=("id", "name")), many=True, dump_only=True)
