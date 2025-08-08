import os
import sys
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
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
EMAIL = os.getenv('EMAIL')
LOCAL_FILEPATH = os.getenv('LOCAL_FILEPATH')

DBT_CLOUD_JOB_ID = os.getenv('DBT_CLOUD_JOB_ID')
DBT_CLOUD_CONN_ID = 'dbt_cloud_default'

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
        region='us-east-1',
        workgroup_name=REDSHIFT_WORKGROUP,
        sql=f"""
        COPY public.newsapi_articles
        FROM 's3://{S3_BUCKET}/{S3_KEY}'
        IAM_ROLE '{REDSHIFT_IAM_ROLE}'
        REGION 'us-east-1'
        FORMAT AS JSON 'auto'
        TIMEFORMAT 'auto';
        """
    )


    dbt_run = DbtCloudRunJobOperator(
        task_id='dbt_run',
        job_id=DBT_CLOUD_JOB_ID,
        dbt_cloud_conn_id=DBT_CLOUD_CONN_ID,
        check_interval=60,
        timeout=300,
        additional_run_config={
            "steps_override": ["dbt run"]
        }
    )

    
    dbt_test = DbtCloudRunJobOperator(
        task_id='dbt_test',
        job_id=DBT_CLOUD_JOB_ID,
        dbt_cloud_conn_id=DBT_CLOUD_CONN_ID,
        check_interval=60,
        timeout=300,
        additional_run_config={
            "steps_override": ["dbt test"]
        }
    )
    
    fetch_task >> copy_to_redshift >> dbt_run >> dbt_test