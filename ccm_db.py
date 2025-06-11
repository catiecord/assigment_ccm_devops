import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Connect to MySQL server
dataBase = mysql.connector.connect(
    host=os.environ.get('MYSQL_HOST', 'localhost'),
    user=os.environ.get('MYSQL_USER', 'root'),
    passwd=os.environ.get('MYSQL_PASSWORD', 'devpass')
)

# Create a cursor object
cursorObject = dataBase.cursor()

# Execute query to create database
cursorObject.execute("CREATE DATABASE IF NOT EXISTS assignment_ccm")

print("Database created successfully!")
