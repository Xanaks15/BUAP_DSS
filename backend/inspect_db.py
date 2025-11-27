from sqlalchemy import create_engine, inspect
from database import SQLALCHEMY_DATABASE_URL
import os

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

from sqlalchemy import create_engine, inspect
from database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables in database:")
for table in tables:
    print(f"- {table}")
    
if "fact_prediccion_proyecto" in tables:
    print("\nColumns in fact_prediccion_proyecto:")
    columns = inspector.get_columns("fact_prediccion_proyecto")
    for column in columns:
        print(f"- {column['name']} ({column['type']})")
