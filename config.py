import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://store_user:yourpassword@localhost:5432/store_status_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False