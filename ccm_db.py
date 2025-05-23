import mysql.connector

# Connect to MySQL server
dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password123'
)

# Create a cursor object
cursorObject = dataBase.cursor()

# Execute query to create database
cursorObject.execute("CREATE DATABASE IF NOT EXISTS assignment_ccm")

print("Database created successfully!")