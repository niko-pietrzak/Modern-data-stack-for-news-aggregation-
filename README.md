# News-aggregation-system-on-AWS
How to run this:
1. Prepare infrastructure: s3 buckets, redshift cluster, roles, permission, schemas, table for data

2. Create and fill .env file, as follows:

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

3. docker-compose build, docker-compose up -d
4. Create airflow user in airflow-webserver container:
    airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email nikodem4799@gmail.com \
		--password admin
4. Prepare 'aws_default' connection with created for Airflow user that has access to Redshift / S3.