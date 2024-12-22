import requests
from flask import Blueprint, jsonify, request
from app.models import Product, Category, ProductCategory, ProductType, Brand, Province, Country
from app.schema import ProductSchema
from sqlalchemy.orm import joinedload
from app.extensions import db
from sqlalchemy import func
import atexit

# import services.app.models.Service

product_blueprint = Blueprint('product_blueprint', __name__)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
BASE_URL = "/products"

SERVICE_INSTANCE = None
appHasRunBefore = False

@product_blueprint.before_app_request
def start_service():
    global SERVICE_INSTANCE, appHasRunBefore
    if not appHasRunBefore:
        service_data = {
            "name": "product",
            "endpoint": "http://127.0.0.1:5001/product",  # Повний URL сервісу продуктів
            "description": "Service for managing products"
        }
        try:
            # Виконати POST-запит на сервіс реєстрації
            response = requests.post(
                url="http://127.0.0.1:5000/services/register",  # Замініть service-host на реальний хост сервісу
                json=service_data
            )
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
            
            # Обробка відповіді
            if response.status_code == 201:
                print("Service registered successfully:", response.json())
                SERVICE_INSTANCE = response.json()
                print(SERVICE_INSTANCE)
            else:
                print("Failed to register service:", response.json())
        
        except requests.exceptions.RequestException as e:
            print("Error during service registration:", str(e))
        
        appHasRunBefore = True


# @product_blueprint.teardown_request
def stop_service(exception=None):
    if SERVICE_INSTANCE is None:
        print("Service instance is not available.")
        return

    try:
        print(SERVICE_INSTANCE)
        response = requests.post(
            url=f"http://127.0.0.1:5000/services/{SERVICE_INSTANCE['id']}/unregister"  # Замініть service-host на реальний хост сервісу
        )
        
        if response.status_code == 200:
            print("Service unregistered successfully.")
        else:
            print(f"Failed to unregister service. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("Error during service unregistration:", str(e))

atexit.register(stop_service)


@product_blueprint.route(BASE_URL, methods=['GET'])
def product_list():
    all_products = Product.query.all()
    return jsonify(products_schema.dump(all_products))


@product_blueprint.route(f"{BASE_URL}/<int:product_id>/", methods=['GET'])
def get_product_by_id(product_id):

    product = Product.query.filter_by(id=product_id).first()

    if not product:
        return jsonify({"error": f"No product found with the id '{product_id}'"}), 404
    product_schema = ProductSchema()
    return jsonify(product_schema.dump(product))

@product_blueprint.route(f"{BASE_URL}/<string:name>/", methods=['GET'])
def get_product_by_name(name):

    product = Product.query.filter(func.lower(Product.name) == name.lower()).first()

    if not product:
        return jsonify({"error": f"No product found with the name '{name}'"}), 404
    product_schema = ProductSchema()
    return jsonify(product_schema.dump(product))


@product_blueprint.route(BASE_URL, methods=['POST'])
def create_product():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        product = Product.create(data)
        
        return jsonify(product_schema.dump(product)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

@product_blueprint.route(f"{BASE_URL}/<int:product_id>/", methods=['PUT'])
def update_product(product_id):
    
    data = request.get_json()

    try:
        updated_product = Product.update(product_id, data)
        product_schema = ProductSchema()
        return jsonify(product_schema.dump(updated_product)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@product_blueprint.route(f"{BASE_URL}/<int:product_id>/", methods=['DELETE'])
def delete_product(product_id):

    product = Product.query.filter(Product.id == product_id).first()
    if product:
        Product.query.filter(Product.id == product_id).delete()
        db.session.commit() 
        return jsonify({"message": f"The product with id {product_id} delete successfully"}), 200
    else:
        return jsonify({"error": "Product not found"}), 400


@product_blueprint.route(f"{BASE_URL}/category/<string:category_name>", methods=['GET'])
def get_product_by_category(category_name):
    category = Category.query.filter(func.lower(Category.category) == category_name.lower()).first()

    if not category:
        return jsonify({"error": f"Category '{category_name}' not found"}), 404

    products = Product.query.join(ProductCategory).filter(ProductCategory.id_category == category.id).all()

    if not products:
        return jsonify({"message": f"No products found for category '{category_name}'"}), 404

    return jsonify(products_schema.dump(products)), 200


@product_blueprint.route(f"{BASE_URL}/type/<string:type>", methods=['GET'])
def get_product_by_type(type):
    type = ProductType.query.filter(func.lower(ProductType.type) == type.lower()).first()

    if not type:
        return jsonify({"error": f"Type '{type}' not found"}), 404

    products = Product.query.filter(Product.id_type == type.id).all()

    if not products:
        return jsonify({"error": f"No products found for type '{type}'"}), 404

    return jsonify(products_schema.dump(products)), 200


@product_blueprint.route(f"{BASE_URL}/add_category", methods=['POST'])
def add_product_category():
    try:
        data = request.json
        product_id = data.get("product")
        categories = data.get("categories")

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({"error": f"No product with id {product_id}"}), 404

        if not categories or not isinstance(categories, list):
            return jsonify({'error': 'Invalid categories input, must be a list'}), 400

        added_categories = []
        for category_id in categories:
            category = Category.query.filter_by(id=category_id).first()
            if not category:
                return jsonify({"error": f"Category with id {category_id} not found"}), 404

            existing_relationship = ProductCategory.query.filter_by(
                id_category=category_id, id_product=product.id
            ).first()
            if existing_relationship:
                continue  

            new_product_category = ProductCategory(id_category=category_id, id_product=product.id)
            db.session.add(new_product_category)
            added_categories.append(category_id)

        if added_categories:
            db.session.commit()
            return jsonify({"message": f"Categories {added_categories} successfully added to product {product_id}"}), 201

        return jsonify({"message": "No new categories were added"}), 200

    except Exception as e:
        db.session.rollback()  
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


@product_blueprint.route(f"{BASE_URL}/sort_by_price", methods=['GET'])
def sort_products_by_price():
    try:
        sort_order = request.args.get('order', 'asc').lower()
        
        if sort_order not in ['asc', 'desc']:
            return jsonify({'error': "Invalid sort order. Use 'asc' or 'desc'"}), 400

        if sort_order == 'asc':
            products = Product.query.order_by(Product.price.asc()).all()
        else:
            products = Product.query.order_by(Product.price.desc()).all()

        products_schema = ProductSchema(many=True) 
        return jsonify(products_schema.dump(products)), 200

    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


@product_blueprint.route(f"{BASE_URL}/brand/<string:brand_name>/", methods=['GET'])
def search_product_by_brand(brand_name):
    """
    Search products by the given brand name.
    """
    try:
        brand = Brand.query.filter(Brand.name.ilike(f"%{brand_name}%")).first()
        
        if not brand:
            return jsonify({"error": f"No brand found with name '{brand_name}'"}), 404

        products = Product.query.filter_by(id_brand=brand.id).all()

        if not products:
            return jsonify({"message": f"No products found for brand '{brand_name}'"}), 404

        products_schema = ProductSchema(many=True)  
        return jsonify(products_schema.dump(products)), 200

    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


# Add Product Type
@product_blueprint.route(f"{BASE_URL}/types", methods=['POST'])
def create_type():
    try:
        data = request.json
        new_type = ProductType(type=data.get('type'))
        db.session.add(new_type)
        db.session.commit()
        return jsonify({"message": "Product Type created", "type": new_type.type}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Get All Product Types
@product_blueprint.route(f"{BASE_URL}/types", methods=['GET'])
def get_types():
    try:
        types = ProductType.query.all()
        return jsonify([{"id": t.id, "type": t.type} for t in types]), 200
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Update Product Type
@product_blueprint.route(f"{BASE_URL}/types/<int:type_id>", methods=['PUT'])
def update_type(type_id):
    try:
        data = request.json
        type_obj = ProductType.query.get_or_404(type_id)
        type_obj.type = data.get('type', type_obj.type)
        db.session.commit()
        return jsonify({"message": "Product Type updated", "type": type_obj.type}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Delete Product Type
@product_blueprint.route(f"{BASE_URL}/types/<int:type_id>", methods=['DELETE'])
def delete_type(type_id):
    try:
        type_obj = ProductType.query.get_or_404(type_id)
        db.session.delete(type_obj)
        db.session.commit()
        return jsonify({"message": "Product Type deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


# Add Category
@product_blueprint.route(f"{BASE_URL}/categories", methods=['POST'])
def create_category():
    try:
        data = request.json
        new_category = Category(category=data.get('category'))
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"message": "Category created", "category": new_category.category}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Get All Categories
@product_blueprint.route(f"{BASE_URL}/categories", methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([{"id": c.id, "category": c.category} for c in categories]), 200
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Update Category
@product_blueprint.route(f"{BASE_URL}/categories/<int:category_id>", methods=['PUT'])
def update_category(category_id):
    try:
        data = request.json
        category = Category.query.get_or_404(category_id)
        category.category = data.get('category', category.category)
        db.session.commit()
        return jsonify({"message": "Category updated", "category": category.category}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Delete Category
@product_blueprint.route(f"{BASE_URL}/categories/<int:category_id>", methods=['DELETE'])
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


# Add Country
@product_blueprint.route(f"{BASE_URL}/country", methods=['POST'])
def create_country():
    try:
        data = request.json
        new_country = Country(country=data.get('country'))
        db.session.add(new_country)
        db.session.commit()
        return jsonify({"message": "Country created", "country": new_country.country}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Get All Countries
@product_blueprint.route(f"{BASE_URL}/countries", methods=['GET'])
def get_countries():
    try:
        countries = Country.query.all()
        return jsonify([{"id": c.id, "country": c.country} for c in countries]), 200
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Update Country
@product_blueprint.route(f"{BASE_URL}/country/<int:country_id>", methods=['PUT'])
def update_country(country_id):
    try:
        data = request.json
        country = Country.query.get_or_404(country_id)
        country.country = data.get('country', country.country)
        db.session.commit()
        return jsonify({"message": "Country updated", "country": country.country}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Delete Country
@product_blueprint.route(f"{BASE_URL}/country/<int:country_id>", methods=['DELETE'])
def delete_country(country_id):
    try:
        country = Country.query.get_or_404(country_id)
        db.session.delete(country)
        db.session.commit()
        return jsonify({"message": "Country deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500


# Add Province
@product_blueprint.route(f"{BASE_URL}/province", methods=['POST'])
def create_province():
    try:
        data = request.json
        new_province = Province(id_country=data.get('id_country'), province=data.get('province'))
        db.session.add(new_province)
        db.session.commit()
        return jsonify({"message": "Province created", "province": new_province.province}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Get All Provinces
@product_blueprint.route(f"{BASE_URL}/provinces", methods=['GET'])
def get_provinces():
    try:
        provinces = Province.query.all()
        return jsonify([{"id": p.id, "province": p.province} for p in provinces]), 200
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Update Province
@product_blueprint.route(f"{BASE_URL}/province/<int:province_id>", methods=['PUT'])
def update_province(province_id):
    try:
        data = request.json
        province = Province.query.get_or_404(province_id)
        province.province = data.get('province', province.province)
        db.session.commit()
        return jsonify({"message": "Province updated", "province": province.province}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Delete Province
@product_blueprint.route(f"{BASE_URL}/province/<int:province_id>", methods=['DELETE'])
def delete_province(province_id):
    try:
        province = Province.query.get_or_404(province_id)
        db.session.delete(province)
        db.session.commit()
        return jsonify({"message": "Province deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500



# Add Brand
@product_blueprint.route(f"{BASE_URL}/brands", methods=['POST'])
def create_brand():
    try:
        data = request.json
        new_brand = Brand(name=data.get('name'), id_country=data.get('id_country'))
        db.session.add(new_brand)
        db.session.commit()
        return jsonify({"message": "Brand created", "brand": new_brand.name}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Get All Brands
@product_blueprint.route(f"{BASE_URL}/brands", methods=['GET'])
def get_brands():
    try:
        brands = Brand.query.all()
        return jsonify([{"id": b.id, "name": b.name} for b in brands]), 200
    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

# Update Brand
@product_blueprint.route(f"{BASE_URL}/brands/<int:brand_id>", methods=['PUT'])
def update_brand(brand_id):
    try:
        data = request.json
        brand = Brand.query.get_or_404(brand_id)
        brand.name = data.get('name', brand.name)
        db.session.commit()
        return jsonify({"message": "Brand updated", "brand": brand.name}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Unexpected error: {str(e)}"}),
