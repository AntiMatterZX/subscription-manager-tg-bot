from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services import ProductService
from app.schemas import product_schema, products_schema

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    products = ProductService.get_all_products()
    return jsonify(products_schema.dump(products)), 200

@product_bp.route('/products/<string:product_id>', methods=['GET'])
def get_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify(product_schema.dump(product)), 200

@product_bp.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
        product = ProductService.create_product(product_data)
        return jsonify(product_schema.dump(product)), 201
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@product_bp.route('/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product_data = product_schema.load(request.json, partial=True)
        product = ProductService.update_product(product_id, product_data)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        return jsonify(product_schema.dump(product)), 200
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@product_bp.route('/products/<string:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        success = ProductService.delete_product(product_id)
        if not success:
            return jsonify({'message': 'Product not found'}), 404
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500