import aiosqlite
import asyncio

class AsyncSQLiteDB:
    # REMEMBER TO ASSIGN A VALUE TO db_path variable in botconfig.py
    def __init__(self, db_path): 
        self.db_path = db_path

    async def connect(self):
        try:
            connection = await aiosqlite.connect(self.db_path)
            return connection
        except aiosqlite.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    async def close(self, connection):
        try:
            if connection:
                await connection.close()
        except aiosqlite.Error as e:
            print(f"Error closing the database connection: {e}")

    # This method is for querying the database
    # Both inserting and fetching data
    async def execute_query(self, query, params=None, fetchall=False):
        # When calling this method to fetch data from db
        # Call it with fetchall argument set to True
        # For example 
        # result = async db.execute_query(my_query, params, fetchall=True)
        connection = await self.connect()
        if not connection:
            return None
        try:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params or [])
                if fetchall:
                    result = await cursor.fetchall()
                    return result
                else:
                    await connection.commit()
        except aiosqlite.Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            await self.close(connection)
