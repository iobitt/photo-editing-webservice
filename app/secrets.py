from dotenv import load_dotenv, dotenv_values


load_dotenv()
config = dotenv_values('.env')


SECRET_KEY = config['SECRET_KEY']
SALT = config['SALT']

DB_USER = config['MONGO_INITDB_ROOT_USERNAME']
DB_PASSWORD = config['MONGO_INITDB_ROOT_PASSWORD']
DB_HOST = config['MONGO_INITDB_DATABASE']
DB_PORT = config['DB_PORT']
DB_NAME = config['DB_NAME']
