from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from ..model.models import User, Order
from ..db.schemas import OrderModel, OrderStatusModel
from ..db.database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

session = Session(bind=engine)


@order_router.get("/")
async def hello(authorize: AuthJWT = Depends()):
    """
    ## A sample hello world route
    This returns Hello world
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    return {"message": "Hello World"}


@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, authorize: AuthJWT = Depends()):
    """
        ## Place an order
        This requires the following
        - quantity : integer
        - pizza_size : String
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    current_user = authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
    )

    new_order.user = user

    session.add(new_order)
    session.commit()

    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status,
    }

    return jsonable_encoder(response)


@order_router.get("/orders")
async def list_all_orders(authorize: AuthJWT = Depends()):
    """
    ## List all orders
    This returns list of all orders
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    current_user = authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()

        return jsonable_encoder(orders)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You are not a superuser"
    )


@order_router.get("/orders/{order_id}")
async def get_order_by_id(order_id: int, authorize: AuthJWT = Depends()):
    """
    ## Get order by id ( Admin )
    This returns Specific order by order_id
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == order_id).first()
        return jsonable_encoder(order)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not allowed to carry out request",
    )


@order_router.get("/user/orders")
async def get_user_orders(authorize: AuthJWT = Depends()):
    """
    ## Get orders by User
    This returns Orders by Specific User
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    return jsonable_encoder(current_user.orders)


@order_router.get("/user/order/{order_id}/")
async def get_specific_order(order_id: int, authorize: AuthJWT = Depends()):
    """
    ## Get Specific Order by order_id
    This returns Hello world
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    orders = current_user.orders

    for o in orders:
        if o.id == order_id:
            return jsonable_encoder(o)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No order with such order Id"
    )


@order_router.put("/order/update/{order_id}/")
async def update_order(order_id: int, order: OrderModel, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    order_to_update = session.query(Order).filter(Order.id == order_id).first()

    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    session.commit()

    response = {
        "id": order_to_update.id,
        "quantity": order_to_update.quantity,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status,
    }

    return jsonable_encoder(response)


@order_router.patch("/order/update/{order_id}/")
async def update_order_status(order_id: int, order: OrderStatusModel, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == order_id).first()
        order_to_update.order_status = order.order_status
        session.commit()

        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status": order_to_update.order_status,
        }
        return jsonable_encoder(response)


@order_router.delete("/order/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )

    order_to_delete = session.query(Order).filter(Order.id == order_id).first()

    if order_to_delete:
        session.delete(order_to_delete)
        session.commit()
        return order_to_delete

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found"
    )
