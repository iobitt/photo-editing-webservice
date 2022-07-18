from dotenv import load_dotenv, dotenv_values


load_dotenv()
config = dotenv_values('.env')


SECRET_KEY = config['SECRET_KEY']
SALT = config['SALT']

DB_USER = config['MONGO_INITDB_ROOT_USERNAME']
DB_PASSWORD = config['MONGO_INITDB_ROOT_PASSWORD']
DB_NAME = config['MONGO_INITDB_DATABASE']
DB_HOST = config['DB_HOST']
DB_PORT = config['DB_PORT']

ADMIN_USERNAME = config['ADMIN_USERNAME']
ADMIN_PASSWORD = config['ADMIN_PASSWORD']

IBM_SSD_MODEL_URL = config['IBM_SSD_MODEL_URL']
