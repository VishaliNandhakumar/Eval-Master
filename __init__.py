from flask import Flask
from flask_mysqldb import MySQL

def create_app():
    app = Flask(__name__)

    # MySQL Config
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Vish@212002' 
    app.config['MYSQL_DB'] = 'user_system'

    mysql = MySQL(app)
    
    return app, mysql
