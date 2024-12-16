from app import db

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)

    products = db.relationship('Product', secondary='product_category', back_populates='categories')

class Province(db.Model):
    __tablename__ = 'province'
    id = db.Column(db.Integer, primary_key=True)
    id_country = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    province = db.Column(db.String(30), nullable=False)

    products = db.relationship('Product', backref='province', lazy=True)


# Country Table
class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(30), nullable=False)

    provinces = db.relationship('Province', backref='country', lazy=True)

class Brand(db.Model):
    __tablename__ = 'brand'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    id_country = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)

    country = db.relationship('Country', backref='brands')

# Product_Type Table
class ProductType(db.Model):
    __tablename__ = 'product_type'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False)

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

# Product_Category Association Table
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id_category = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)