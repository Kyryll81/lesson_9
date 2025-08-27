from json import JSONDecodeError, dumps
from unittest.mock import patch, mock_open, MagicMock

import pytest

from order_manager import (get_json, save_json, get_orders, add_order, delete_order, update_orders)

# Didn't used it

def open_and_close():
    print("BEGING")
    print("COMMIT")
    yield
    print("END")


# Tests for get_json
@patch("builtins.open", new_callable=mock_open, read_data=dumps([{
    "name": "Іван", 
    "product": "Ноутбук", 
    "quantity": 1}]))
def test_get_json(mock_open) -> None:
    data: list[dict] = [{
        "name": "Іван",
        "product": "Ноутбук",
        "quantity": 1
    }]

    result: list[dict] = get_json()
    
    mock_open.assert_called_once_with("db/orders.json", "r")
        
    assert result == data


@pytest.mark.parametrize("exception", [
    JSONDecodeError,
    ValueError,
    TypeError,
    Exception
])
@patch("builtins.open", new_callable=mock_open, read_data="")
@patch("json.load")
def test_get_json_exceptions(mock_json_load, mock_open_file, exception):
    mock_json_load.side_effect = JSONDecodeError("msg", "doc", 0) if exception is JSONDecodeError else exception()
    
    with pytest.raises(exception):
        get_json()

    mock_open_file.assert_called_once_with("db/orders.json", "r")


# Tests for save_json
def test_save_json():
    database_data: list[dict] = [{"name": "Alice", "product": "Book", "quantity": 1}]
    new_data: list[dict] = [{"name": "Bob", "product": "Pen", "quantity": 2}]
    combined_data: list[dict] = database_data + new_data
    
    with patch("order_manager.get_json", return_value=database_data) as mock_get_json:
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_json_dump:
                save_json(new_data)
                mock_get_json.assert_called_once()
                
                mock_file.assert_called_once_with("db/orders.json", "w")
                
                mock_json_dump.assert_called_once_with(combined_data, mock_file())


# AI generated
@pytest.mark.parametrize(
    "exception,except_msg", [
        (ValueError, "Raised value error."),
        (Exception, "Raised unkown exception."),
])
def test_save_json_dump_error(exception, except_msg):
    exsisting_data: list = [{"name": "Alice", "product": "Book", "quantity": 1}]
    new_data = [{"name": "Bob", "product": "Pen", "quantity": 2}]
    
    
    with patch("order_manager.get_json", return_value=exsisting_data) as mock_get_json, \
         patch("builtins.open") as mock_file, \
         patch("json.dump", side_effect=exception(except_msg)) as mock_json_dump:
             
            with pytest.raises(exception) as exception_info:
                 save_json(new_data)
            
            assert str(exception_info.value) == except_msg
            
            mock_file.assert_called_once_with("db/orders.json", "w")
            mock_get_json.assert_called_once()


#test get orders
@pytest.fixture
def mock_get_json(monkeypatch) -> list[dict]:
    data = [
        {"name": "Іван", "product": "Ноутбук", "quantity": 1},
        {"name": "Оля", "product": "Мишка", "quantity": 2}
    ]
    monkeypatch.setattr("order_manager.get_json", lambda: data)
    return data


def test_get_orders_by_name(mock_get_json, capsys) -> None:
    get_orders(name="Оля")
    captured = capsys.readouterr()
    assert "Оля | Мишка | 2" in captured.out


def test_get_orders_by_product(mock_get_json, capsys) -> None:
    get_orders(product="Ноутбук")
    captured = capsys.readouterr()
    assert "Іван | Ноутбук | 1" in captured.out


def test_get_orders_by_quantity(mock_get_json, capsys) -> None:
    get_orders(quantity=2)
    captured = capsys.readouterr()
    assert "Оля | Мишка | 2" in captured.out


def test_get_orders_no_match(mock_get_json, capsys) -> None:
    get_orders()
    captured = capsys.readouterr()
    assert "" in captured.out

#test add order
@pytest.fixture
def mock_save_json(monkeypatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("order_manager.save_json", mock)
    return mock

@pytest.fixture
def mock_get_json(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("order_manager.get_json", mock)
    return mock


def test_add_order_all(mock_save_json):
    data: list[dict] = [{"name": "Іван", "product": "Ноутбук", "quantity": 1}]
    add_order(name="Іван", product="Ноутбук", quantity=1)
    mock_save_json.assert_called_once_with(data) 


#test delete order
def test_delete_order_with_no_id(mock_get_json, mock_save_json):
    data: list[dict] = [
        {"name": "Іван", "product": "Ноутбук", "quantity": 1},
        {"name": "Оля", "product": "Мишка", "quantity": 2}
        ]
    mock_get_json.return_value = data.copy()
    delete_order()
    expected_data = data.copy()
    expected_data.pop(-1)
    mock_save_json.assert_called_once_with(expected_data)


def test_delete_order_with_valid_index(mock_get_json, mock_save_json, capsys):
    data: list[dict] = [
        {"name": "Іван", "product": "Ноутбук", "quantity": 1},
        {"name": "Оля", "product": "Мишка", "quantity": 2}
        ]
    mock_get_json.return_value = data.copy()
    
    delete_order(0)
    
    expected_data = data.copy()
    expected_data.pop(0)
    
    mock_save_json.assert_called_once_with(expected_data)
    
    captured = capsys.readouterr()
    assert "Order 0 is deleated." in captured.out


def test_delete_order_with_invalid_index(mock_get_json, mock_save_json, capsys):
    data: list[dict] = [
        {"name": "Іван", "product": "Ноутбук", "quantity": 1},
        {"name": "Оля", "product": "Мишка", "quantity": 2}
        ]
    mock_get_json.return_value = data.copy()
    
    delete_order(10)
    captured = capsys.readouterr()
    assert "Id is not valid." in captured.out

    mock_save_json.assert_not_called()


def test_delete_order_with_exception(mock_get_json, mock_save_json):
    mock_get_json.return_value = [
        {"name": "Іван", "product": "Ноутбук", "quantity": 1},
        {"name": "Оля", "product": "Мишка", "quantity": 2}
        ]
    
    with pytest.raises(TypeError):
        delete_order("")
    
    mock_save_json.assert_not_called()


# update orders
def test_update_orders(mock_save_json, capsys):
    updated_data = [
        {"name": "Іван", "product": "Ноутбук", "quantity": 1},
        {"name": "Оля", "product": "Мишка", "quantity": 2},
        {"name": "Микола", "product": "Мишка", "quantity": 10}
        ]
    
    update_orders(updated_data)
    captured = capsys.readouterr()
    assert "Database is updated." in captured.out
    
    mock_save_json.assert_called_once()


def test_update_orders_type_error(mock_save_json):    
    with pytest.raises(TypeError):
        update_orders("")
    
    mock_save_json.assert_not_called()
