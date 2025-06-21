For this project we will be using SQLite.
We follow this procedure to install/create the database

### **Create the database**

#### adding packages

* python-dotenv 1.1.0
* psycopg2-binary 2.9.10
* re-create environments with the scripts in the setup folder OR
* update .toml and poetry.lock for both environments
    * poetry add Flask Flask-SQLAlchemy Flask-Migrate python-dotenv psycopg2-binary
    * poetry install --no-root

#### .env

Create a .env file in the poetry folder:
DATABASE_FILENAME:poetry.db
DATABASE_URL=sqlite:///poetry.db
SQLALCHEMY_DATABASE_URI="${DATABASE_URL}"

#### Create the database using flask-migrate

Add the following to the .env file:
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_FILENAME:poetry.db
DATABASE_URL=sqlite:///poetry.db
SQLALCHEMY_DATABASE_URI="${DATABASE_URL}"

Now, from your project root (where `pyproject.toml` lives), initialize and apply your initial migration:

* Create the migrations folder and generate an initial schema (note: normally this is not needed as the migrations
  folder and database versions are included in git:
    * '"'**_poetry run flask db init_**'"'
* Generate an update script for the initial database from dbModel.py with
    * 'poetry run flask db migrate -m "Initial schema"'
* Create the .db in the subfolder '**_instance_**' file with
    * 'poetry run flask db upgrade*'

### Altering the model

* Generate an update script with
    * 'poetry run flask db migrate -m "My changes"'
      * examples: "Add [table], add [column] to [table]'
* Upgrade the database with
    * 'poetry run flask upgrade*'





