import json

def get_json() -> list[dict]:
    with open("db/orders.json", "r") as f:
        return json.load(f)


def save_json(data: list) -> None:
    db: list = get_json()
    db.extend(data)
    with open("db/orders.json", "w") as f:
        json.dump(db, f)


def get_orders(name: str = "", product: str = "", quantity: int = 0) -> None:
    orders: list[dict] = get_json()
    for order in orders:
        if any([val in order.values() for val in (name, product, quantity) if val]):
            print(f"{order.get("name")} | {order.get("product")} | {order.get("quantity")}") 


def add_order(name: str = "", product: str = "", quantity: int = 0) -> None:
    data: list[dict] = [{
        "name": name,
        "product": product,
        "quantity": quantity,
    }]
    save_json(data)


def delete_order(id: int = -1) -> None:
    orders: list[dict] = get_json()
    if orders and len(orders) > id:
        orders.pop(id)
        save_json(orders)
        print(f"Order {id} is deleated.")
    else:
        print("Id is not valid.")


def update_orders(orders: list[dict]) -> None:
    
    if not isinstance(orders, list):
        raise TypeError
    
    save_json(orders)
    print("Database is updated.")


def main() -> None:
    get_orders()


if __name__ == "__main__":
    main()
