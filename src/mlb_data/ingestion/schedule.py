from mlb_data.api.statsapi import get_data
from datetime import datetime

BRONZE_SCHEMA = "mlb.bronze"
TABLES = {
    "game_schedule": f"{BRONZE_SCHEMA}.schedule"
}

def get_schedule(day):
    """
    Get the MLB game schedule for a specific day.

    Args:
        day (str): The date in 'YYYY-MM-DD'
    Returns:
        list: A list of games scheduled for the specified day.
        timestamp: The timestamp of the schedule retrieval.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schedule = get_data(
        url_v="1", 
        endpoint="schedule", 
        params=[
                ("sportId", 1), 
                ("date", day)
            ]
        )
    schedule = schedule.get("dates", [])

    return schedule, timestamp

def process_schedule(schedule, timestamp):
    """
    Process the MLB game schedule data.

    Args:
        schedule (list): A list of games scheduled for a specific day.
    Returns:
        df: A DataFrame of processed game information.
    """
    processed_schedule = []
    for day in schedule:
        games = day.get("games", [])
        for game in games:
            game_info = {
                "game_pk": game.get("gamePk"),
                "game_type": game.get("gamedayType"),
                "game_status": game.get("status", {}).get("codedGameState", "X"),
                "last_update_timestamp": timestamp,
                "is_post_day_reprocessed": False,
                "post_day_reprocessed_timestamp": None
            }
            processed_schedule.append(game_info)

    processed_schedule_df = spark.createDataFrame(processed_schedule)
    processed_schedule_df = processed_schedule_df.filter(
        (processed_schedule_df.game_pk.isNotNull()) & 
        (processed_schedule_df.game_type.isNotNull())
    )

    return processed_schedule_df

def write_or_update_schedule(processed_schedule_df):
    """
    Write or update the MLB game schedule data in the database.

    Args:
        processed_schedule_df (DataFrame): A DataFrame containing processed game information.
    """
    sql = f"""
        MERGE INTO {TABLES['game_schedule']} AS target
        USING {processed_schedule_df._jdf.schema} AS source
        ON target.game_pk = source.game_pk

        WHEN MATCHED
            AND target.status in ('S', 'P', 'D')
            AND target.status != source.status
        THEN UPDATE SET
            target.game_status = source.game_status,
            target.last_update_timestamp = source.last_update_timestamp

        WHEN NOT MATCHED
        THEN INSERT (
            game_pk,
            game_type,
            game_status,
            last_update_timestamp,
            is_post_day_reprocessed,
            post_day_reprocessed_timestamp
        )
        VALUES (
            source.game_pk,
            source.game_type,
            source.game_status,
            source.last_update_timestamp,
            source.is_post_day_reprocessed,
            source.post_day_reprocessed_timestamp
        );
    """
    spark.sql(sql)

if __name__ == "__main__":
    day = datetime.now().strftime("%Y-%m-%d")

    schedule, timestamp = get_schedule(day)
    processed_schedule = process_schedule(schedule, timestamp)
    write_or_update_schedule(processed_schedule)