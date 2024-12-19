from flask import Blueprint, jsonify, request
from app.models import Product, Category, ProductCategory, ProductType, Brand
from app.schema import ProductSchema
from sqlalchemy.orm import joinedload
from app.extensions import db
from sqlalchemy import func

product_blueprint = Blueprint('product_blueprint', __name__)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
BASE_URL = "/products"

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
