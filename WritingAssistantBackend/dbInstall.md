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
DATABASE_URL=sqlite:///poetry.db
#### Create the database using flask-migrate
Add the following to the .env file:
FLASK_APP=app.py
FLASK_ENV=development

Now go to the WritingAssistantBackend folder and initialize the migrations folder with '**_poetry run flask --app app.py db init_**'
 (creates the migrations folder) and generate an initial schema with 
'**_poetry run flask --app app.py db migrate -m "Initial schema"_**' and '**_poetry run flask db upgrade_**'
to create poetry.db in the subfolder '**_instance_**'.

### Adding tables
* Create a models.py file and import it in app.py (after initialisation of the database)
* Generate a new migration with '**_poetry run flask --app app.py db migrate -m Add "table1, table2, ..."_**' (note: adding a column to a table = add column1 to table1)
* Verify the auto-generated script in the new script in migrations/versions
* Apply changes to the database with '**_poetry run flask --app app.py db upgrade_**'

Use
* **_poetry run flask --app app.py db migrate -m "Your message"_**
* **_poetry run flask --app app.py db upgrade_**
for each update cycle




