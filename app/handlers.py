from fastapi import APIRouter, Body, Depends, Query, HTTPException
from typing import List

from app.forms import ProductForm, DishForm, RecipesForm, OrderForm, Status, OrderEditForm
from app.models import connect_db, Products, Dish, Recipes, Orders, OrderDish, PFE

router = APIRouter()


# Запрос на добавление продукта
@router.post('/products/add', name='product:add', tags=["products"])
def add_prod(
        prod_forms: List[ProductForm] = Body(..., embed=True),
        database=Depends(connect_db)):
    somelist = ''
    for prod_form in prod_forms:
        exists_prod = database.query(Products.id).filter(Products.name == prod_form.name).first()
        if exists_prod:
            exists_prod = database.query(Products).filter(Products.name == prod_form.name).first()
            exists_prod.amount += prod_form.amount
            database.commit()
            somelist += f'Количество продукта обновлено, prod_id: {exists_prod.id}; '
        else:
            new_prod = Products(
                name=prod_form.name,
                amount=prod_form.amount,
                unit_type=prod_form.unit_type
            )
            database.add(new_prod)
            database.commit()
            somelist += f'Добавлено на склад, prod_id: {new_prod.id}; '
    return somelist


# Запрос всех продуктов
@router.get('/products/get', name='product:get', tags=["products"])
def get_prod(database=Depends(connect_db)):
    all_prod = database.query(Products).all()
    return all_prod


# Запрос на добавление блюда
@router.post('/dish/add', name='dish:add', tags=["dish"])
def add_dish(
        dish_forms: List[DishForm] = Body(..., embed=True),
        database=Depends(connect_db)):
    somelist = ''
    for dish_form in dish_forms:
        exists_dish = database.query(Dish).filter(Dish.name == dish_form.name).one_or_none()
        if exists_dish:
            somelist += f'Уже в меню, prod_id: {exists_dish.id}; '
        else:
            new_dish = Dish(
                name=dish_form.name,
                price=dish_form.price,
                info=dish_form.info
            )
            database.add(new_dish)
            database.commit()
            somelist += f'Добавлено в меню, prod_id: {new_dish.id}; '
    return somelist


@router.get('/dish/get', name='dish:get', tags=["dish"])
def get_dish(database=Depends(connect_db)):
    return database.query(Dish).all()


# Запрос на добавление рецепта
@router.post('/recipe/add', name='recipe:add', tags=["recipe"])
def add_recipe(
        recipes_forms: List[RecipesForm] = Body(..., embed=True),
        database=Depends(connect_db)):
    for recipe_form in recipes_forms:
        dish = database.query(Dish).filter(Dish.name == recipe_form.dish_name).first()
        for prod_name in recipe_form.prods_names:
            prod = database.query(Products).filter(Products.name == prod_name.name).first()
            new_recipe = Recipes(
                dish_id=dish.id,
                prod_id=prod.id,
                prod_amount=prod_name.amount
            )
            database.add(new_recipe)
            database.commit()
    return {'status': 'ok'}


@router.get('/recipe/get', name='recipe:get', tags=["recipe"])
def get_recipe(database=Depends(connect_db),
               dish_id: int = Query(..., description="id блюда")):
    dish_recipe = database.query(Recipes).filter(Recipes.dish_id == dish_id).all()
    if not dish_recipe:
        raise HTTPException(status_code=404, detail="id блюда не найден")
    else:
        return dish_recipe


# Запрос на добавление заказа
@router.post('/orders/add', name='order:add', tags=["orders"])
def add_order(
        order_forms: List[OrderForm] = Body(..., embed=True),
        database=Depends(connect_db)):
    for order_form in order_forms:
        new_order = Orders(
            PFE_id=order_form.pfe_id

        )
        pfe = database.query(PFE).get(order_form.pfe_id)
        pfe.empty = False
        database.add(new_order)
        database.commit()
        for prod_name in order_form.dish_ides:
            dish = database.query(Dish).filter(Dish.id == prod_name.dish_id).first()
            new_orderDish = OrderDish(
                order_id=new_order.id,
                dish_id=dish.id,
                quantity=prod_name.amount
            )
            database.add(new_orderDish)
            database.commit()
    return {'status': 'ok'}


# Запрос на изменение статуса заказа на "В процессе"
@router.put('/orders/take', name='order:take', tags=["orders"])
def take_order(
        order_id: int = Query(..., description="id заказа"),
        database=Depends(connect_db)):
    order = database.query(Orders).get(order_id)
    if order.status != 'not_ready':
        return {'status': 'Заказ не был взят или уже готов'}
    else:
        order.status = 'in_progress'
        database.commit()
        return {'status': 'ok'}


# Запрос на изменение статуса заказа на "Готов"
@router.put('/orders/complete', name='order:complete', tags=["orders"])
def complete_order(
        order_id: int = Query(..., description="id заказа"),
        database=Depends(connect_db)):
    order = database.query(Orders).get(order_id)
    if order.status == 'in_progress':
        order.status = 'ready'
        '''all_dish = database.query(OrderDish).filter(OrderDish.order_id == order_id).all()
        for dish in all_dish:
            for i in range(dish.quantity):
                dish_id = dish.dish_id
                all_prod = database.query(Recipes).filter(Recipes.dish_id == dish_id).all()
                for prod in all_prod:
                    prod_on_bd = database.query(Products).filter(Products.id == prod.prod_id).first()
                    prod_on_bd.amount -= prod.prod_amount
                    database.commit()
        return {'status': 'ok'}'''
    else:
        return {'status': 'Заказ не был взят или уже готов'}


# Запрос на вывод заказов с различными статусами
@router.get('/orders/statuses', name='orders:statuses', tags=["orders"])
def order_statuses(
        order_status: Status = Query(..., description="Статус заказов"),
        database=Depends(connect_db)):
    if order_status.value == '-':
        return database.query(Orders).all()
    orders = database.query(Orders).filter(Orders.status == order_status.value).all()
    return orders


# Запрос на получение комплектации заказа
@router.get('/orders/pack', name='orders:pack', tags=["orders"])
def order_pack(
        order_id: int = Query(..., description="id заказа"),
        database=Depends(connect_db)):
    packs = database.query(OrderDish).filter(OrderDish.order_id == order_id).all()
    if not packs:
        raise HTTPException(status_code=404, detail="id заказа не найден")
    new_packs = []
    for pack in packs:
        new_packs.append(f'id: {pack.dish_id}, amount: {pack.quantity}, status: {pack.status}')
    return new_packs


# Запрос на редактирование заказа
@router.post('/orders/edit', name='orders:edit', tags=["orders"])
def order_edit(
        order_edit_form: OrderEditForm = Body(..., embed=True, description='Список позиций требуемых'
                                                                           'для включения или удаления'),
        database=Depends(connect_db)):
    packs = database.query(Orders).filter(Orders.id == order_edit_form.order_id).one_or_none()
    if not packs:
        raise HTTPException(status_code=404, detail="id заказа не найден")
    for dish in order_edit_form.dish:
        editing = database.query(OrderDish).filter(OrderDish.order_id == order_edit_form.order_id,
                                                   OrderDish.dish_id == dish.dish_id).first()

        if dish.amount != 0 and editing:
            editing.quantity = dish.amount
            database.commit()
        else:
            database.query(OrderDish).filter(OrderDish.order_id == order_edit_form.order_id,
                                             OrderDish.dish_id == dish.dish_id
                                             ).delete(synchronize_session='fetch')
            database.commit()
    return 'good'


# Блюдо в процесс готовки
@router.put('/kitchen/take', name='dish:take', tags=["kitchen"])
def dish_take(
        order_id: int = Query(..., description="id заказа"),
        dish_id: int = Query(..., description="id блюда"),
        database=Depends(connect_db)):
    dish_to_take = database.query(OrderDish).filter(OrderDish.order_id == order_id,
                                                    OrderDish.dish_id == dish_id).first()
    if not dish_to_take:
        raise HTTPException(status_code=404, detail="Не найдено блюдо, либо заказ")
    elif dish_to_take.status == 'not_ready':
        dish_to_take.status = 'in_progress'
        database.commit()
        for i in range(dish_to_take.quantity):
            all_prod = database.query(Recipes).filter(Recipes.dish_id == dish_id).all()
            for prod in all_prod:
                prod_on_bd = database.query(Products).filter(Products.id == prod.prod_id).first()
                prod_on_bd.amount -= prod.prod_amount
                database.commit()
        return f'{dish_to_take.dish_id} статус обновлен на {dish_to_take.status}'
    else:
        return {'status': 'блюдо было взято или уже готово'}


# Блюдо отметить как готовое
@router.put('/kitchen/complete', name='dish:complete', tags=["kitchen"])
def dish_complete(
        order_id: int = Query(..., description="id заказа"),
        dish_id: int = Query(..., description="id блюда"),
        database=Depends(connect_db)):
    dish_to_complete = database.query(OrderDish).filter(OrderDish.order_id == order_id,
                                                        OrderDish.dish_id == dish_id).first()
    if not dish_to_complete:
        raise HTTPException(status_code=404, detail="Не найдено блюдо, либо заказ")
    elif dish_to_complete.status == 'in_progress':
        dish_to_complete.status = 'ready'
        database.commit()
        other_dish = database.query(OrderDish).filter(OrderDish.order_id == order_id).all()
        for od in other_dish:
            if od.status != 'ready':
                return f'id {dish_to_complete.dish_id} статус обновлен на {dish_to_complete.status}'
        order = database.query(Orders).filter(Orders.id == order_id).first()
        order.status = 'ready'
        database.commit()
        return f'id {dish_to_complete.dish_id} статус обновлен на {dish_to_complete.status} ' \
               f'{dish_to_complete.order_id} заказ готов'
    else:
        return f'Блюдо id {dish_to_complete.dish_id} еще не начали готовить, либо уже готово'


# Запрос на вывод блюд с различными статусами
@router.get('/kitchen/statuses', name='dish:statuses', tags=["kitchen"])
def dish_statuses(
        dish_status: Status = Query(..., description="Статус блюд"),
        database=Depends(connect_db)):
    if dish_status.value == '-':
        return database.query(OrderDish).all()
    all_dish = database.query(OrderDish).filter(OrderDish.status == dish_status.value).all()
    return all_dish


'''@router.put('/kitchen/take/status', name='dish:take', tags=["kitchen"])
def dish_take(database=Depends(connect_db)):
    dish = database.query(OrderDish).all()
    for d in dish:
        d.status = 'not_ready'
        database.commit()
    return 'ok'
'''


# Запрос на удаление определенных строк в таблицах
@router.delete('/test', name='test:add', tags=["test"])
def add_test(test_form: List[str] = Query(..., description="Скок угодно"), database=Depends(connect_db)):
    database.query(Recipes).filter(
        Recipes.dish_id == 1
    ).delete(synchronize_session='fetch')
    database.commit()
    return {'test': test_form}


# Запрос на добавление столика в бд
@router.post('/pfe/add', name='pfe:add', tags=["pfe"])
def add_pfe(pfe_form: int = Query(..., description="Скок надо"), database=Depends(connect_db)):
    for i in range(pfe_form):
        new_PFE = PFE(
            empty=True
        )
        database.add(new_PFE)
        database.commit()
    return {'status': 'ok'}


# Запрос на вывод всех столиков
@router.get('/pfe/get', name='pfe:get', tags=["pfe"])
def get_pfe(database=Depends(connect_db)):
    return database.query(PFE).all()


# Запрос на изменение статуса столика
@router.put('/pfe/status', name='pfe:status', tags=["pfe"])
def change_pfe(database=Depends(connect_db),
               pfe_id: int = Query(..., description="id столика"),
               pfe_status: bool = Query(..., description="обновленный статус столика")):
    pfe_to_edit = database.query(PFE).filter(PFE.id == pfe_id).first()
    if not pfe_to_edit:
        raise HTTPException(status_code=404, detail="id столика не найден")
    pfe_to_edit.empty = pfe_status
    database.commit()
    return f'{pfe_to_edit.id} статус занятости обновлен на {pfe_to_edit.empty}'


"""
{
  "recipes_forms": [
    {
      "dish_name": "Пицца 4 сыра",
      "prods_names": [
        {
          "name": "сыр Моцарелла",
          "amount": 100
        },
        {
          "name": "сыр Эмменталь",
          "amount": 100
        },
        {
          "name": "сыр Горгонзола",
          "amount": 50
        },
        {
          "name": "сыр Пармезан",
          "amount": 50
        }
      ]
    }
  ]
}

{
  "prod_forms": [
    {
      "name": "сыр Моцарелла",
      "amount": 20000,
      "unit_type": "грамм"
    },
    {
      "name": "сыр Эмменталь",
      "amount": 20000,
      "unit_type": "грамм"
    },
    {
      "name": "сыр Горгонзола",
      "amount": 20000,
      "unit_type": "грамм"
    },
    {
      "name": "сыр Пармезан",
      "amount": 20000,
      "unit_type": "грамм"
    }
  ]
}
"""
