import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from app.models import StoreStatus, BusinessHours, Timezone
from app.extensions import db
from app import create_app

def load_csv_to_db(csv_file, table_class):
    app = create_app() 
    with app.app_context():
        try:
            df = pd.read_csv(csv_file)  
            df.columns = [col.strip() for col in df.columns]
            records = df.to_dict(orient='records')
            db.session.bulk_insert_mappings(table_class, records)
            db.session.commit()
            print(f"Data successfully loaded into the {table_class.__tablename__} table.")
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")
            db.session.rollback()

if __name__ == "__main__":
    load_csv_to_db('data/store_status.csv', StoreStatus)
    load_csv_to_db('data/menu_hours.csv', BusinessHours)
    load_csv_to_db('data/timezone.csv', Timezone)


