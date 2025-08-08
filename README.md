# Modern data stack for news aggregation

I took my first data project done entirely on AWS and adjusted it to use modern data stack: DWH (Redshift), Airflow Orchestration, DBT Cloud.

How to run this:
1. Prepare infrastructure: s3 buckets, redshift cluster, roles, permission, schemas, table for data

2. Configure models in Dbt Cloud with necessary aws/redshift configuration.

3. Create and fill .env file, as follows:

        # Airflow variables
        AIRFLOW__CORE__LOAD_EXAMPLES=False
        AIRFLOW__LOGGIN__REMOTE_LOGGING=False
        AIRFLOW__WEBSERVER__SECRET_KEY=<your-hashed-secret-key>

        # NewsAPI
        NEWS_API_KEY=<your-api-from-newsapi-website>

        # S3
        S3_BUCKET=<s3-bucket-name>
        S3_KEY=<file-key>

        # Redshift
        REDSHIFT_IAM_ROLE=<arn-redshift-role>
        REDSHIFT_DATABASE=<database-name>
        REDSHIFT_WORKGROUP=<workgroup-name>
        REDSHIFT_TABLE=<schema.table-name>
        REDSHIFT_REGION=<your-redshift-region>

        LOCAL_FILEPATH=/tmp/news_data.json
        EMAIL=<your-email-for-airflow-notifications>

        # DBT
        DBT_CLOUD_JOB_ID=<your-dbt-job-with-dbt-run-and-test>

4. docker-compose build, docker-compose up -d
5. Create airflow user in airflow-webserver container:
    airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email mail@gmail.com \
		--password admin
6. Create AWS User for Airflow with Redshift / S3 permissions
7. Configure 'aws_default' connection.
