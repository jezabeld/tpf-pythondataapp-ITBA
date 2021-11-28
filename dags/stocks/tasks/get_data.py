"""Get stock data."""
import argparse
from sqlalchemy import event, DDL
from utils.models import StockValue
from utils.db_connections import PostgresClient
import json
import requests
from time import sleep
from datetime import datetime

def keys_in_db(pg_cli, symbol, date):
    query = f"""select count(*) from stock_value
                where symbol = '{symbol}' and date = '{date}'"""
    r = pg_cli.execute(query).fetchone()
    rbool = (dict(r)['count'] == 1)
    return rbool

def get_data_from_api(api_url, api_key, symbol, date, historic, STOCK_FN='TIME_SERIES_DAILY'):
    size = '&outputsize=full' if historic else ''
    end_point = (
        f"{api_url}?function={STOCK_FN}&symbol={symbol}"
        f"&apikey={api_key}{size}&datatype=json"
    )
    r = requests.get(end_point)
    data = json.loads(r.content)
    return data

def insert_to_db(data, user, passw, db_url, db_name):
    """Inserts data into db if not exists. """
    pg_cli = PostgresClient(db_name, user, passw, db_url)
    session = pg_cli.get_session()
    if isinstance(data,StockValue) and (not keys_in_db(pg_cli, **data.get_keys()) ):
        session.add(data)
    elif isinstance(data,list):
        [session.add(item) for item in data if isinstance(item,StockValue) and (not keys_in_db(pg_cli, **item.get_keys()) )]
    else:
        pass
    session.commit()


def get_data_to_db(user, passw, db_url, db_name, api_url, api_key, symbol, date, historic=False):
    """Program entrypoint."""
    print(historic)
    data = get_data_from_api(api_url, api_key, symbol, date, historic)
    #sleep(61)  # To avoid api limits
    if historic:
        model_data = [StockValue(symbol=symbol, date=fecha, open= dic['1. open'], close= dic['4. close'], high= dic['2. high'], low= dic['3. low'], volume = dic['5. volume']) 
                    for fecha, dic in data["Time Series (Daily)"].items()]
    else:
        if datetime.strptime(date, '%Y-%m-%d').weekday() < 5: #weekdays
            dic = data["Time Series (Daily)"][date]
            model_data = StockValue(symbol=symbol, date=date, open= dic['1. open'], close= dic['4. close'], high= dic['2. high'], low= dic['3. low'], volume = dic['5. volume'])
        else: #weekend
            print("No data because is weekend.")
            model_data = []

    insert_to_db(model_data, user, passw, db_url, db_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DB connection")
    parser.add_argument("--user", type=str, help="USER")
    parser.add_argument("--passw", type=str, help="PASSWORD")
    parser.add_argument("--db_url", type=str, help="DB_URL")
    parser.add_argument("--db_name", type=str, help="DB_NAME")
    parser.add_argument("--api_url", type=str, help="api_url")
    parser.add_argument("--api_key", type=str, help="api_key")
    parser.add_argument("--symbol", type=str, help="symbol")
    parser.add_argument("--date", type=str, help="date")
    parser.add_argument("--historic", type=bool, help="historic", default=False)
    params = parser.parse_args()
    get_data_to_db(params.user, params.passw, params.db_urn, params.db_name, 
        params.api_url, params.api_key, params.symbol, 
        params.date, params.historic)