from app.extensions import ma
from app.models import *

class ProductSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Product
        load_instance = True
        include_relationships = True

class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category

class ProvinceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Province

class CountrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Country

class BrandSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Brand

class ProductType(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductType

class ProductCategory(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductCategory