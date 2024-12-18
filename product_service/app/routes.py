from flask import Blueprint, jsonify, request
from app.models import Product
from app.schema import ProductSchema

product_blueprint = Blueprint('product_blueprint', __name__)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
BASE_URL = "/products"

@product_blueprint.route(BASE_URL)
def product_list():
    all_products = Product.query.all()
    return jsonify(products_schema.dump(all_products))
    # return jsonify({"message": "List of products"})

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
