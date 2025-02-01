from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
project_dir = os.path.abspath(os.path.join(os.getcwd(), 'database/dbtables'))
os.makedirs(project_dir, exist_ok=True)
DATABASE_URL = f"sqlite:///{project_dir}/hubberlin.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()