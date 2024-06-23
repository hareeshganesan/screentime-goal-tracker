import sqlite3
from os.path import expanduser, exists
import os
from datetime import datetime, timedelta
import pytz

def query_database(start_date=None, end_date=None, devices=None):
    # Get the path to the database
    knowledge_db = expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")
    
    # Check if the file exists
    if not exists(knowledge_db):
        raise FileNotFoundError(f"Database file not found at {knowledge_db}")
    
    # Check file permissions
    if not os.access(knowledge_db, os.R_OK):
        raise PermissionError(f"No read permission for database file at {knowledge_db}")
    
    try:
        with sqlite3.connect(knowledge_db) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            
            # Base query
            query = """
            SELECT
                ZOBJECT.ZVALUESTRING AS "app", 
                (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "usage",
                (ZOBJECT.ZSTARTDATE + 978307200) as "start_time", 
                (ZOBJECT.ZENDDATE + 978307200) as "end_time",
                (ZOBJECT.ZCREATIONDATE + 978307200) as "created_at", 
                ZOBJECT.ZSECONDSFROMGMT AS "tz",
                ZSOURCE.ZDEVICEID AS "device_id",
                ZMODEL AS "device_model"
            FROM
                ZOBJECT 
                LEFT JOIN
                ZSTRUCTUREDMETADATA 
                ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
                LEFT JOIN
                ZSOURCE 
                ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
                LEFT JOIN
                ZSYNCPEER
                ON ZSOURCE.ZDEVICEID = ZSYNCPEER.ZDEVICEID
            WHERE
                ZSTREAMNAME = "/app/usage"
            """
            
            params = []
            
            # Add date range filter if specified
            if start_date:
                query += " AND ZOBJECT.ZSTARTDATE + 978307200 >= ?"
                params.append(start_date.timestamp())
            if end_date:
                query += " AND ZOBJECT.ZENDDATE + 978307200 <= ?"
                params.append(end_date.timestamp())
            
            # Add device filter if specified
            if devices:
                device_filter = " AND ZSOURCE.ZDEVICEID IN ({})".format(','.join(['?']*len(devices)))
                query += device_filter
                params.extend(devices)
            
            query += " ORDER BY ZSTARTDATE DESC"
            
            # Execute the query
            cur.execute(query, params)
            
            # Fetch all rows from the result set
            rows = cur.fetchall()

            # Convert times to local time zone
            local_tz = pytz.timezone('America/New_York')  # Default to New York, but we'll use the actual local time

            converted_rows = []
            for row in rows:
                row = dict(row)
                for time_field in ['start_time', 'end_time', 'created_at']:
                    utc_time = datetime.utcfromtimestamp(row[time_field])
                    local_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
                    row[time_field] = local_time
                converted_rows.append(row)

            return converted_rows

    except sqlite3.Error as e:
        raise Exception(f"SQLite error: {e}")

# Example usage:
# all_data = query_database()
# filtered_data = query_database(start_date=datetime(2023, 6, 1), end_date=datetime(2023, 6, 30), devices=['device_id_1', 'device_id_2'])