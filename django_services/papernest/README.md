# Papernest exercise by Alberto Jaen

## Solution

Steps taken to solve the exercise:

1. Created a [script](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/scripts/process_init_data.py) to process the data provided and transform Lambert coordinates to degrees (latitude and longitude).
2. Created new app called [operators](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/) inside the Papernest Django application to contain all the business logic for this exercise.
3. Created two DB models: [Operator and Coverage](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/models.py). Operator holds the available operators in the initial dataset. Coverage holds all the geographical points where we have data on the coverage for different operators.
4. Created [Django command](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/management/management/commands/init_db.py) to load the data into the DB. It will only run if it detects the database hasn't been initialized yet.
5. Created [two views](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/views.py) inside the operators app: a generic list view for the Operator model and a function-based view that retrieves the coverage of the operators based on the textual address.
6. Installed the [GIS extension and the necessary libraries](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/Dockerfile#11) in the Django server to be able to use geographical objects in the database.
7. Developed unit tests for critical logic:
    - Function based view with [exercise's logic](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/tests/test_views.py).
    - [Logic that queries the model](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/tests/test_models.py) to find the nearest coverages to the coordinates provided.
    - [Lambert function](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/operators/scripts/tests/test_utils.py) used in initial script to transform Lambert's coordinates to degrees.

The code is statically typed with mypy and formatted with black. These constraints are enforced with [precommit](https://github.com/ajaen4/django-serverless/blob/main/.pre-commit-config.yaml).

## How it works

The endpoint to request coverages for a certain textual address is /operators/coverage/. This endpoint has as a mandatory parameter called "q" where the textual address should be provided. The endpoint only accepts incoming GET methods.

Once the method is called it executes an HTTP request to the API provided and retrieves the latitude and longitude of the address. It then queries the table of coverages to find the nearest record, if it exists, that is at most 200 meters away from the address given. Finally, it returns as a JSON object the coverages for each provider found.

## Deployment models

The Django application can be deployed in 3 ways: using the built in Django development server, using docker compose and deploying to AWS.

### Django local development server

This mode uses the manage.py runserver command and deploys the Django server and the database on the same instance. This is the only case where we don't use a Postgres database, SQLite is used.

**One important consideration is that you will need to install [GDAL](https://gdal.org/index.html) locally.**

These are the following commands needed to run:

```bash
# Navigate to the papernest Django project
cd django_services/papernest
# Process file
python3 operators/scripts/process_init_data.py
# Run migrations to create tables in db
python3 manage.py makemigrations
python3 manage.py migrate
# Initialize database
python3 manage.py init_db
# Run server 
python3 manage.py runserver
```

### Docker compose

This mode uses docker compose to run a Postgres db and Django application on different containers. You can find the docker compose file [here](https://github.com/ajaen4/django-serverless/blob/main/django_services/papernest/compose.yaml).

**One important consideration is that you migth need to run the command 'docker compose up' a second time if the Django app is deployed before the Postgres database is ready to accept incoming requests.**

These are the following commands needed to run it:

```bash
# Navigate to the papernest Django project
cd django_services/papernest
# Run servers 
docker compose up
```

### AWS

This mode uses pulumi to deploy to AWS. It will deploy a Postgres RDS database and a Load Balancer + ECS service to host the Django application.

**One important consideration is that you will need to install the [Pulumi CLI](https://www.pulumi.com/docs/install/) locally and [create a stack](https://www.pulumi.com/docs/concepts/stack/#:~:text=To%20create%20a%20new%20stack,yaml%20file.) for the project**

These are the following commands needed to run it:

```bash
# Navigate to the pulumi directory
cd iac/
## Deploy with Pulumi
pulumi up
```

When the command finishes it will output the domain of our Django project, you can use it to query the endpoint. More details about this deployment can be found in the root [README.md](https://github.com/ajaen4/django-serverless/blob/main/README.md)

## Possible improvements

- The Django server uses HTTP, which is not safe. It should use HTTPS by generating and setting an SSL certificate.
- The Django server hosts the endpoints and the static files server, these should be separated.
- Only the most critical tests have been included as unitary tests for simplicity purposses, but these should be extended.