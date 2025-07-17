import os
import sys
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from datetime import datetime, timedelta

sys.path.append('/opt/airflow/scripts')
from fetch_news import fetch_newsapi_data, save_to_local

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_KEY = os.getenv('S3_KEY')
REDSHIFT_IAM_ROLE = os.getenv('REDSHIFT_IAM_ROLE')
REDSHIFT_DATABASE = os.getenv('REDSHIFT_DATABASE')
REDSHIFT_WORKGROUP= os.getenv('REDSHIFT_WORKGROUP')
REDSHIFT_TABLE= os.getenv('REDSHIFT_TABLE')
REDSHIFT_REGION= os.getenv('REDSHIFT_REGION')
EMAIL = os.getenv('EMAIL')
LOCAL_FILEPATH = os.getenv('LOCAL_FILEPATH')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': [EMAIL],
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'newsapi_pipeline',
    default_args=default_args,
    description='Fetch news from NewsAPI and upload to S3 + Redshift',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['newsapi', 's3', 'redshift'],
) as dag:

    def fetch_and_store():
        data = fetch_newsapi_data(api_key=NEWS_API_KEY)
        path = save_to_local(data, LOCAL_FILEPATH)

        s3_hook = S3Hook(aws_conn_id='aws_default')
        s3_hook.load_file(
            filename=path,
            key=S3_KEY,
            bucket_name=S3_BUCKET,
            replace=True
        )
        print(f"Uploaded to s3://{S3_BUCKET}/{S3_KEY}")

    fetch_task = PythonOperator(
        task_id='fetch_and_upload_newsapi',
        python_callable=fetch_and_store
    )

    copy_to_redshift = RedshiftDataOperator(
        task_id='copy_data_to_redshift',
        database=REDSHIFT_DATABASE,
        region=REDSHIFT_REGION,
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        COPY {REDSHIFT_TABLE}
        FROM 's3://{S3_BUCKET}/{S3_KEY}'
        IAM_ROLE '{REDSHIFT_IAM_ROLE}'
        REGION '{REDSHIFT_REGION}'
        FORMAT AS JSON 'auto'
        TIMEFORMAT 'auto';
        """
    )

    fetch_task >> copy_to_redshift


    # run_dbt = BashOperator(
    #     task_id='run_dbt_models',
    #     bash_command='cd /opt/airflow/dbt/newsapi_dbt && dbt run'
    # )