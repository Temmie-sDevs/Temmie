class Table:
    def __init__(self, db_connection, table_name, pk_columns):
        self.db = db_connection
        self.cursor = self.db.cursor
        self.table_name = table_name
        self.pk_columns = pk_columns if isinstance(pk_columns, (list, tuple)) else [pk_columns]

    def insert(self, data: dict):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.db.connection.commit()

    def delete(self, **kwargs):
        """
        kwargs = {pk_col: value}
        """
        where_clause = " AND ".join([f"{col}=?" for col in kwargs.keys()])
        values = tuple(kwargs.values())
        query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
        self.cursor.execute(query, values)
        self.db.connection.commit()

    def get(self, **kwargs):
        """
        kwargs = {column: value} for filtering (optional)
        """
        if kwargs:
            where_clause = " AND ".join([f"{col}=?" for col in kwargs.keys()])
            values = tuple(kwargs.values())
            query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
            self.cursor.execute(query, values)
        else:
            query = f"SELECT * FROM {self.table_name}"
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def update(self, data: dict, **filters):
        """
        Updates one or more rows in the table.

        Example:
            update({"username": "JohnDoe"}, id=123)

        data: dict -> columns to update
        filters: dict -> columns to filter on (WHERE)
        """
        if not data:
            raise ValueError("No data provided for update.")

        set_clause = ", ".join([f"{col}=?" for col in data.keys()])
        values = list(data.values())

        if filters:
            where_clause = " AND ".join([f"{col}=?" for col in filters.keys()])
            values.extend(filters.values())
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"
        else:
            query = f"UPDATE {self.table_name} SET {set_clause}"

        self.cursor.execute(query, tuple(values))
        self.db.connection.commit()