from utils.db_connections import PostgresClient
from datetime import datetime, timedelta
import os
import pandas as pd


def get_data_from_db():
    """Get data from database. """
    db_name = os.getenv('DATABASE_NAME')
    user = os.getenv('DATABASE_USERNAME')
    passw = os.getenv('DATABASE_PASSWORD')
    db_url = os.getenv('DATABASE_URL')

    pg_cli = PostgresClient(db_name, user, passw, db_url)
    sql = "select * from postgres.stock_value" #.format(date=date)
    data = pg_cli.to_frame(sql).squeeze()

    return data

def transform_data(data, execution_date):
    """ Compute a 7 day rolling average and filter data."""
    data[ '7day_rolling_avg' ] = data.sort_values(['symbol', 'date']).groupby('symbol')['close'].transform(lambda x: x.rolling(7).mean())
    data['date'] = pd.to_datetime(data['date'])
    filt_data = data[data['date'] >= datetime.strptime(execution_date, '%Y-%m-%d')- timedelta(days=7)]

    return filt_data