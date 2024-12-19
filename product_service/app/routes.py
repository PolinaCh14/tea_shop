from flask import Blueprint, jsonify, request
from app.models import Product
from app.schema import ProductSchema
from sqlalchemy.orm import joinedload
from app.extensions import db

product_blueprint = Blueprint('product_blueprint', __name__)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
BASE_URL = "/products"

@product_blueprint.route(BASE_URL, methods=['GET'])
def product_list():
    all_products = Product.query.all()
    return jsonify(products_schema.dump(all_products))


@product_blueprint.route(f"{BASE_URL}/<int:product_id>/", methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)

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
        return jsonify({"message": f"The product with id {product_id} delete succsesfuly"}), 200
    else:
        return jsonify({"error": "Product not found"}), 400