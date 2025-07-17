# Configuration
PROJECT_NAME=airflow_project
AIRFLOW_UID=50000

# Docker Compose
up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build --no-cache

# Airflow Setup
create-admin:
	docker-compose run --rm airflow-cli \
		airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email nikodem4799@gmail.com \
		--password admin

reset-db:
	docker-compose run --rm airflow-cli airflow db reset -y

# Airflow Commands
logs:
	docker-compose logs -f

list-dags:
	docker-compose run --rm airflow-cli airflow dags list

list-tasks:
	docker-compose run --rm airflow-cli airflow tasks list $(dag)

trigger:
	docker-compose run --rm airflow-cli airflow dags trigger $(dag)

# Cleanup
clean:
	sudo rm -rf ./dags/__pycache__ ./logs ./plugins/__pycache__