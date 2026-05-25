from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'delivery-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='delivery_optimization_pipeline',
    default_args=default_args,
    description='Daily Delivery Optimization Pipeline',
    schedule='0 1 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['delivery', 'ml', 'pipeline'],
) as dag:

    t1 = BashOperator(
        task_id='generate_data',
        bash_command='echo "Task 1: Generate Data - OK"',
    )

    t2 = BashOperator(
        task_id='run_analysis',
        bash_command='echo "Task 2: Run Analysis - OK"',
    )

    t3 = BashOperator(
        task_id='run_ml_model',
        bash_command='echo "Task 3: Run ML Model - OK"',
    )

    t1 >> t2 >> t3