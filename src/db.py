import os

import pyodbc


def connect():
    """Create a SQL Server connection from environment variables."""
    driver = os.getenv("LIBRARY_DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("LIBRARY_DB_SERVER", "localhost")
    database = os.getenv("LIBRARY_DB_NAME", "SmartLibrary")
    trusted = os.getenv("LIBRARY_DB_TRUSTED_CONNECTION", "yes")
    connection_string = (
        f"Driver={{{driver}}};"
        f"Server={server};"
        f"Database={database};"
        f"Trusted_Connection={trusted};"
    )
    return pyodbc.connect(connection_string)
