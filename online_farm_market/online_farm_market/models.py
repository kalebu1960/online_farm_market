from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base

# -------------------- USER --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    @staticmethod
    def get_all(db):
        return db.query(User).all()

    @staticmethod
    def get_by_id(db, user_id):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db, username, email):
        user = User(username=username, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id

    @staticmethod
    def update(db, user_id, username, email):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.username = username
            user.email = email
            db.commit()
            return True
        return False

    @staticmethod
    def delete(db, user_id):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

# -------------------- FARMER --------------------
class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)

    @staticmethod
    def get_all(db):
        return db.query(Farmer).all()

    @staticmethod
    def get_by_id(db, farmer_id):
        return db.query(Farmer).filter(Farmer.id == farmer_id).first()

    @staticmethod
    def create(db, name, location):
        farmer = Farmer(name=name, location=location)
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        return farmer.id

    @staticmethod
    def update(db, farmer_id, name, location):
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if farmer:
            farmer.name = name
            farmer.location = location
            db.commit()
            return True
        return False

    @staticmethod
    def delete(db, farmer_id):
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if farmer:
            db.delete(farmer)
            db.commit()
            return True
        return False

# -------------------- PRODUCT --------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))

    @staticmethod
    def get_all(db):
        return db.query(Product).all()

    @staticmethod
    def get_by_id(db, product_id):
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def create(db, name, price, farmer_id):
        product = Product(name=name, price=price, farmer_id=farmer_id)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product.id

    @staticmethod
    def update(db, product_id, name, price, farmer_id):
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.name = name
            product.price = price
            product.farmer_id = farmer_id
            db.commit()
            return True
        return False

    @staticmethod
    def delete(db, product_id):
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
            return True
        return False

# -------------------- CUSTOMER --------------------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    @staticmethod
    def get_all(db):
        return db.query(Customer).all()

    @staticmethod
    def get_by_id(db, customer_id):
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def create(db, name, email):
        customer = Customer(name=name, email=email)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer.id

    @staticmethod
    def update(db, customer_id, name, email):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.name = name
            customer.email = email
            db.commit()
            return True
        return False

    @staticmethod
    def delete(db, customer_id):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            db.delete(customer)
            db.commit()
            return True
        return False

# -------------------- TRANSACTION --------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def get_all(db):
        return db.query(Transaction).all()

    @staticmethod
    def get_by_id(db, transaction_id):
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def create(db, customer_id, product_id, quantity, total=None):
        if total is None:
            db_product = db.query(Product).filter(Product.id == product_id).first()
            total = db_product.price * quantity
        transaction = Transaction(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            total=total
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction.id

    @staticmethod
    def update(db, transaction_id, customer_id, product_id, quantity):
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            transaction.customer_id = customer_id
            transaction.product_id = product_id
            transaction.quantity = quantity
            db_product = db.query(Product).filter(Product.id == product_id).first()
            transaction.total = db_product.price * quantity
            db.commit()
            return True
        return False

    @staticmethod
    def delete(db, transaction_id):
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False
