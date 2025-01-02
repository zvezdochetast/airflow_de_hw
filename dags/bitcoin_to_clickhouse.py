# Bitcoin Api To Clickhouse DAG
# 2024-12-30

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.hooks.base import BaseHook
import requests
import logging
from clickhouse_driver import Client

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ClickHouse connection details
CLICKHOUSE_CONN_ID = 'clickhouse_yc'
CLICKHOUSE_TABLE = 'analytics'

# API endpoint for fetching Bitcoin rates
API_URL = 'https://api.coincap.io/v2/rates/bitcoin'

# Function to fetch data from API
def get_bitcoin_rate():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        print(data)
        return {
            'id': data['data']['id'],
            'symbol': data['data']['symbol'],
            'currencySymbol': data['data'].get('currencySymbol'),
            'type': data['data']['type'],
            'rateUsd': float(data['data']['rateUsd']),
            'timestamp': int(datetime.utcnow().timestamp() * 1000),
        }
    except Exception as e:
        logging.error(f"Error fetching data from API: {e}")
        raise

# Function to insert data into ClickHouse
def insert_into_clickhouse(**context):
    # Retrieve the entire response data from XCom
    parameters = context['task_instance'].xcom_pull(task_ids='get_bitcoin_rate')

    # Get connection params from Airflow
    connection = BaseHook.get_connection(CLICKHOUSE_CONN_ID)

    try:
        client = Client(
            host=connection.host,
            port=connection.port,
            user=connection.login,
            password=connection.password,
            database=connection.schema,
            secure=True,
            verify=True,
            ca_certs='/usr/local/share/ca-certificates/Yandex/RootCA.crt'
        )

        query = f"""
        INSERT INTO {CLICKHOUSE_TABLE} (id, symbol, currencySymbol, type, rateUsd, timestamp)
        VALUES
        (%(id)s, %(symbol)s, %(currencySymbol)s, %(type)s, %(rateUsd)s, %(timestamp)s)
        """
        client.execute(query, parameters)
        logging.info("Data inserted successfully into ClickHouse.")
    except Exception as e:
        logging.error(f"Error inserting data into ClickHouse: {e}")
        raise


# Define the DAG
dag = DAG(
    'bitcoin_to_clickhouse',
    default_args=default_args,
    description='Fetch Bitcoin rate from API and store in ClickHouse',
    schedule_interval='*/30 * * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
)

# Define the tasks
get_bitcoin_rate_task = PythonOperator(
    task_id='get_bitcoin_rate',
    python_callable=get_bitcoin_rate,
    dag=dag,
)

insert_into_clickhouse_task = PythonOperator(
    task_id='insert_into_clickhouse',
    python_callable=insert_into_clickhouse,
    provide_context=True,
    dag=dag,
)

# Set up task dependencies
get_bitcoin_rate_task >> insert_into_clickhouse_task

