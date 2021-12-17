"""Stocks Data Daily DAG."""
from datetime import datetime, timedelta
import os
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.papermill.operators.papermill import PapermillOperator

from stocks.tasks.create_tables import init_db
from stocks.tasks.get_data import get_data_to_db

# Env vars and definitions
USER = os.getenv('DATABASE_USERNAME')
PASSWORD = os.getenv('DATABASE_PASSWORD')
DB_URL = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('DATABASE_NAME')

API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')

STOCKS = {'google': 'goog', 'microsoft': 'msft', 'amazon': 'amzn'}

ROOT_DIR = Path(__file__).parent.resolve()

# Dag definition
with DAG(
    "stocksData_dag",
    schedule_interval='0 5 * * *',
    start_date=datetime(2021, 10, 11),
    catchup=False,
) as dag:
    create_tables = PythonOperator(
        task_id="create_tables",
        python_callable=init_db,
        op_kwargs={
            'user': USER,
            'passw': PASSWORD,
            'db_url': DB_URL,
            'db_name': DB_NAME,
        },
    )
    get_stock_data = {}
    for company, symbol in STOCKS.items():
        get_stock_data[company] = PythonOperator(
            task_id=f'get_daily_data_{company}',
            python_callable=get_data_to_db,
            op_kwargs={
                'user': USER,
                'passw': PASSWORD,
                'db_url': DB_URL,
                'db_name': DB_NAME,
                'api_url': API_URL,
                'api_key': API_KEY,
                'symbol': symbol,
                'date': '{{ ds }}',
                'historic': True,
            },
        )

    notebook_task = PapermillOperator(
        task_id="notebook_task",
        input_nb= str(ROOT_DIR/"tasks/stock_plot.ipynb"),
        output_nb= str(ROOT_DIR/"tasks/stock_plot_executed.ipynb"),
        parameters={"execution_date": "{{ ds }}"},
    )

# Dag workflow
    create_tables >> [task for task in get_stock_data.values()] >> notebook_task