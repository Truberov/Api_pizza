from typing import List

from pydantic import BaseModel, Field
from pydantic.types import Enum


class Status(Enum):
    nothing = '-'
    in_progress = 'in_progress'
    ready = 'ready'
    not_ready = 'not_ready'


class ProductForm(BaseModel):
    name: str = Field(..., max_length=64, description='Имя не должно быть больше 64 символов в длинну')
    amount: int = Field(...)
    unit_type: str


class DishForm(BaseModel):
    name: str = Field(..., max_length=64, description='Имя не должно быть больше 64 символов в длинну')
    price: int
    info: str


class PDForm(BaseModel):
    name: str
    amount: int


class RecipesForm(BaseModel):
    dish_name: str
    prods_names: List[PDForm]


class ODForm(BaseModel):
    dish_id: int
    amount: int


class DForm(BaseModel):
    dish_id: int
    amount: int


class OrderForm(BaseModel):
    pfe_id: int
    dish_ides: List[ODForm]


class OrderEditForm(BaseModel):
    order_id: int
    dish: List[DForm] = Field(..., description='Что требуется удалить или добавить в заказ')
