import pymongo

from app.secrets import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

connect_url = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
client = pymongo.MongoClient(connect_url)
db = client[DB_NAME]

db.users.create_index("email", unique=True)
