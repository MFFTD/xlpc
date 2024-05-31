import botconfig
from typing import Any
from utils.db import AsyncSQLiteDB

db = AsyncSQLiteDB(botconfig.db_path)

# This function inserts the data that we want to save for persistent views(buttons) that will persist on bot restarts
# message id is required by Discord to make a view persist 
async def insert_challenge_message_data_to_db(message_id, author, team_name) -> None:
    try:
        insert_message_id_query = "INSERT INTO message (message_id, author, team_name) VALUES (?, ?, ?)"
        params = (message_id, author, team_name)
        await db.execute_query(insert_message_id_query, params)
    except Exception as e:
        print(f"An error occurred while inserting message_ids: {e}")
        return

# This function gets the data that we want for the persistent views
async def fetch_challenge_message_data() -> list[dict[str, Any]]:
    try:
        fetch_message_ids_query = "SELECT message_id, author, team_name FROM message"
        result = await db.execute_query(fetch_message_ids_query, fetchall=True)
        message_data = [{"message_id": row[0],"author": row[1], "team_name": row[2]} for row in result]
        print(f"printing message data\n: {message_data}")
        return message_data
    except Exception as e:
        print(f"An error occurred while fetching message_ids: {e}")
        return []

