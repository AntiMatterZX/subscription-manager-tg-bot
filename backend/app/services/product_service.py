from app import db
from app.models import Product
from sqlalchemy.exc import SQLAlchemyError

class ProductService:
    @staticmethod
    def get_all_products():
        return Product.query.all()
    
    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get(product_id)
    
    @staticmethod
    def create_product(product_data):
        try:
            product = Product(
                name=product_data['name'],
                description=product_data.get('description')
            )
            db.session.add(product)
            db.session.commit()
            return product
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_product(product_id, product_data):
        try:
            product = Product.query.get(product_id)
            if not product:
                return None
            
            product.name = product_data.get('name', product.name)
            product.description = product_data.get('description', product.description)
            
            db.session.commit()
            return product
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_product(product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return False
            
            db.session.delete(product)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e