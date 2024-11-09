from typing import Any, Dict, List, Optional
import sqlite3
import json

class Database:
    """Base database class for VAPT scanner."""

    def __init__(self, db_path: str):
        """Initialize database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of query results
        """
        if not self.connection:
            self.connect()

        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def commit(self) -> None:
        """Commit changes to database."""
        if self.connection:
            self.connection.commit()

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """Create a new table if it doesn't exist.

        Args:
            table_name: Name of the table
            columns: Dictionary of column names and their SQL types
        """
        cols = ", ".join([f"{name} {type_}" for name, type_ in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})"
        self.execute_query(query)
        self.commit()
