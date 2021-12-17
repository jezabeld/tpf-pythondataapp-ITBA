import pytest
from stocks.tasks.get_data import keys_in_db, get_data_from_api, insert_to_db
from utils.models import StockValue
from utils.db_connections import PostgresClient

symbol = "symbol"
date = "date"
db_name = "db_name" 
user = "user" 
passw = "passw" 
db_url = "db_url"

@pytest.mark.parametrize("count, expected_result", [(1, True), (0, False)])
def test_keys_in_db(count, expected_result):
    print("[Test Get Data - Keys in DB] should return true if data keys exists in database or False otherwise.")

    returned_keys = {
        "count": count
    }

    class pg_cli_mock(object):
        def execute(*args):
            class ex_mock(object):
                def fetchone(*args):
                    return returned_keys
            
            return ex_mock()

    pg_cli = pg_cli_mock()
    assert keys_in_db(pg_cli, symbol, date) == expected_result

def test_get_data_from_api(mocker):
    print("[Test Get Data - Get Data From API] should convert API request to python dict.")

    class responseMock:
        pass

    response_returned = responseMock()
    response_returned.content = '{"data": "result"}'
    expected_data = {
        "data": "result"
    }
    mocker.patch('stocks.tasks.get_data.requests.get', return_value = response_returned)

    assert get_data_from_api(api_url="", api_key="", symbol=symbol, date=date, historic=False) == expected_data

test_cases_for_insert = [
       ([StockValue(symbol, date, 1, 1, 1, 1, 1),
           StockValue(symbol, date, 2, 2, 2, 2, 2),
           StockValue(symbol, date, 3, 3, 3, 3, 3),
           StockValue(symbol, date, 4, 4, 4, 4, 4)], 4), 
        (StockValue(symbol, date, 1, 1, 1, 1, 1), 1),
        ([StockValue(symbol, date, 1, 1, 1, 1, 1),
           StockValue(symbol, date, 2, 2, 2, 2, 2),
           "string",
           StockValue(symbol, date, 4, 4, 4, 4, 4)], 3),
        ("string", 0),
    ]

@pytest.mark.parametrize("data, expected_result", test_cases_for_insert)
def test_insert_to_db_insert(mocker, data, expected_result):
    print("[Test Get Data - Insert Data to DB] should insert data into database.")

    class SessionMock:
        def __init__(self):
            self.data = []
        def add(self, x):
            self.data.append(x)
        def commit(self):
            pass
      
    sessMock = SessionMock()
    
    mocker.patch.object(PostgresClient, "get_session", return_value=sessMock)
    mocker.patch("stocks.tasks.get_data.keys_in_db", return_value=False)
    mocker.patch('stocks.tasks.get_data.PostgresClient', return_value = PostgresClient)

    insert_to_db(data, user, passw, db_url, db_name)
    assert len(sessMock.data) == expected_result


