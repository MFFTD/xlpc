import botconfig
from utils.db import AsyncSQLiteDB

db = AsyncSQLiteDB(botconfig.db_path)

async def check_if_team_leader(author) -> Optional[str]:
    try:
        check_if_team_leader_query = "SELECT team_name FROM team WHERE team_leader = ?"
        params = (author,)
        result = await db.execute_query(check_if_team_leader_query, params, fetchall=True)
        
        if not result:
            return None

        team_name = result[0][0]
        return team_name
    except Exception as e:
        await interaction.response.send_message("Error inviting to the team")
        print(f"Error inviting user to the team: {e}")
        return None
