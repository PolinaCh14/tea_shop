# from app import db
from app.extensions import db

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)

    products = db.relationship('Product', secondary='product_category', back_populates='categories')

    def __init__(self, category):
        self.category = category

class Province(db.Model):
    __tablename__ = 'province'
    id = db.Column(db.Integer, primary_key=True)
    id_country = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    province = db.Column(db.String(30), nullable=False)

    products = db.relationship('Product', backref='province', lazy=True)

    def __init__(self, id_country, province):
        self.id_country = id_country
        self.province = province

class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(30), nullable=False)

    provinces = db.relationship('Province', backref='country', lazy=True)

    def __init__(self, country):
        self.country = country

class Brand(db.Model):
    __tablename__ = 'brand'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    id_country = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)

    country = db.relationship('Country', backref='brands')

    def __init__(self, name, id_country):
        self.name = name
        self.id_country = id_country

class ProductType(db.Model):
    __tablename__ = 'product_type'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False)

    def __init__(self, type):
        self.type = type

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    id_brand = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    id_type = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(200))
    properties = db.Column(db.String(40))
    taste = db.Column(db.String(30))
    appearance = db.Column(db.String(50))
    id_province = db.Column(db.Integer, db.ForeignKey('province.id'), nullable=False)

    brand = db.relationship('Brand', backref='products')
    type = db.relationship('ProductType', backref='products')
    categories = db.relationship('Category', secondary='product_category', back_populates='products')

    def __init__(self, weight, id_brand, id_type, name, description, properties, taste, appearance, id_province):
        self.weight = weight
        self.id_brand = id_brand
        self.id_type = id_type
        self.name = name
        self.description = description
        self.properties = properties
        self.taste = taste
        self.appearance = appearance
        self.id_province = id_province
    
    @staticmethod
    def create(data):
        """
        Create new instanse in db
        """
        try:
            new_product = Product(
                weight=data.get('weight'),
                id_brand=data.get('id_brand'),
                id_type=data.get('id_type'),
                name=data.get('name'),
                description=data.get('description'),
                properties=data.get('properties'),
                taste=data.get('taste'),
                appearance=data.get('appearance'),
                id_province=data.get('id_province')
            )
            db.session.add(new_product)  # Додаємо об'єкт до сесії
            db.session.commit()  # Комітимо зміни до бази даних
            return new_product
        except Exception as e:
            db.session.rollback()  # У разі помилки відкочуємо транзакцію
            raise ValueError(f"Error creating product: {str(e)}")
    
    @staticmethod
    def update(product_id, data):
        """
        Update an existing product in the database.
        """
        try:
            # Find the product by ID
            product = Product.query.get_or_404(product_id)
        
            # Update fields from the provided data
            if 'weight' in data:
                product.weight = data.get('weight')
            if 'id_brand' in data:
                product.id_brand = data.get('id_brand')
            if 'id_type' in data:
                product.id_type = data.get('id_type')
            if 'name' in data:
                product.name = data.get('name')
            if 'description' in data:
                product.description = data.get('description')
            if 'properties' in data:
                product.properties = data.get('properties')
            if 'taste' in data:
                product.taste = data.get('taste')
            if 'appearance' in data:
                product.appearance = data.get('appearance')
            if 'id_province' in data:
                product.id_province = data.get('id_province')

        # Commit changes to the database
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            raise ValueError(f"Error updating product: {str(e)}")


        

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id_category = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)

    def __init__(self, id_category, id_product):
        self.id_category = id_category
        self.id_product = id_product
