from datetime import datetime
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from app.config import DATABASE_URL

Base = declarative_base()


def connect_db():
    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
    session = Session(bind=engine.connect())
    return session


class Unit(Enum):
    KGRM = 'kgram'
    PIECES = 'pieces'
    NOTHING = '-'


class Status(Enum):
    in_progress = 'in_progress'
    ready = 'ready'
    not_ready = 'not_ready'
    done = 'done'


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    amount = Column(Integer)
    unit_type = Column(String, default=Unit.NOTHING.value)
    added_at = Column(String, default=datetime.utcnow())


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    info = Column(String)


class Recipes(Base):
    __tablename__ = 'recipes'
    dish_id = Column(Integer, ForeignKey('dish.id'))
    prod_id = Column(Integer, ForeignKey('products.id'))
    prod_amount = Column(Integer)
    recipe_pk = Column(Integer, primary_key=True)


class PFE(Base):
    __tablename__ = 'pfe'
    id = Column(Integer, primary_key=True)
    empty = Column(Boolean, default=True)


class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    PFE_id = Column(Integer, ForeignKey('pfe.id'))
    added_at = Column(String, default=datetime.utcnow())
    status = Column(String, default=Status.not_ready.value)

class OrderDish(Base):
    __tablename__ = 'order_dish'
    order_pk = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))
    quantity = Column(Integer, default=1)
    status = Column(String, default=Status.not_ready.value)
