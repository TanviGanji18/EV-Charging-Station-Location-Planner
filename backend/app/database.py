import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
engine=create_engine(URL.create('postgresql+psycopg',username=os.getenv('DB_USER'),password=os.getenv('DB_PASSWORD'),host=os.getenv('DB_HOST'),port=int(os.getenv('DB_PORT','5432')),database=os.getenv('DB_NAME','postgres')),connect_args={'sslmode':'require','connect_timeout':10},pool_pre_ping=True)
Session=sessionmaker(bind=engine)
def db():
    with Session() as session:
        yield session
