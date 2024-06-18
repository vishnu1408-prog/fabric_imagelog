import psycopg2



class Execute:
    def __init__(self):
        self.keepalive_kwargs = {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 5,
            "keepalives_count": 5,
        }
        self.conn = self.connect()

    def connect(self):
        conn = psycopg2.connect(
            database="knitting",
            user="postgres",
            password="55555",
            host="127.0.0.1",
            port="5432",
            **self.keepalive_kwargs
        )
        conn.autocommit = True
        return conn

    def insert(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            return True
        except Exception as e:
            print(str(e))
            return False

    def insert_return_id(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            id = cur.fetchone()[0]
            cur.close()
            return id
        except Exception as e:
            print(str(e))
            return False

    def select(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            rows = [
                dict((cur.description[i][0], value) for i, value in enumerate(row))
                for row in cur.fetchall()
            ]
            cur.close()
            return rows

        except Exception as e:
            print(str(e))
            return False
        
    def select_list(self,query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            return rows

        except Exception as e:
            print(str(e))
            return False

    def update(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            return True
        except Exception as e:
            print(str(e))
            return False

    def delete(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            cur.close()
            return True
        except Exception as e:
            print(str(e))
            return False


class DayReportDb:
    def __init__(self):
        self.execute = Execute()

    def get_roll_name(self, rollId):
        try:
            query = (
                "SELECT roll_name FROM public.roll_details WHERE roll_id='"
                + rollId
                + "'ORDER BY roll_id"
            )
            data = self.execute.select(query)
            return data[0]["roll_name"]

        except Exception as e:
            print(str(e))
            return False

    def get_machine_name(self):
        try:
            query = (
                "SELECT machinedtl_name FROM public.machine_details ORDER BY machinedtl_id ASC "
            )
            data = self.execute.select(query)
            return data[0]["machinedtl_name"]
        except Exception as e:
            print(str(e))
            return False
        
    def get_timestamp_defect_type(self,current_date):
        try:
            query = (
                "SELECT "
                "dd.timestamp AS timestamp, "
                "dt.defect_name AS defect_type "
                "FROM defect_details dd "
                "JOIN alarm_status AS a ON a.defect_id = dd.defect_id "
                "JOIN defect_type AS dt ON dd.defecttyp_id = dt.defecttyp_id "
                "WHERE dd.timestamp >= '" + str(current_date) + "' "
                "AND dd.timestamp < '" + str(current_date) + "'::timestamp + interval '1 day' "
                "ORDER BY dd.timestamp;"
            )
            data = self.execute.select_list(query)

            return data
        except Exception as e:
            print(str(e))
            return False

    def get_rotation_per_hour(self,current_date):
        try:
            query = (
                "SELECT DATE(timestamp) AS date, "
                "EXTRACT(HOUR FROM timestamp) AS hour, "
                "COUNT(*) AS rotation_count "
                "FROM rotation_details "
                "WHERE timestamp >= '" + str(current_date) + "' "
                "AND timestamp < '" + str(current_date) + "'::timestamp + interval '1 day' "
                "GROUP BY date, hour "
                "ORDER BY date, hour;"
            )
            data = self.execute.select_list(query)

            return data
        except Exception as e:
            print(str(e))
            return False      

    def get_roll_details_records(self,current_date):
        try:
            query = (
                        "WITH LastEntry AS ("
                        "SELECT MAX(timestamp) AS last_entry_timestamp "
                        "FROM roll_details "
                        "WHERE DATE(timestamp) = '" + str(current_date) + "'::date - interval '1 day'"
                        ")"
                        "SELECT "
                        "roll_number, "
                        "DATE(timestamp) AS roll_start_date, "
                        "EXTRACT(HOUR FROM timestamp) || ':' || EXTRACT(MINUTE FROM timestamp) || ':' || EXTRACT(SECOND FROM timestamp) AS roll_start_time, "
                        "order_no, "
                        "roll_name, "
                        "revolution "
                        "FROM roll_details "
                        "WHERE DATE(timestamp) = '" + str(current_date) + "'::date OR timestamp = (SELECT last_entry_timestamp FROM LastEntry) "
                        "ORDER BY timestamp ASC;"
                    )
            data = self.execute.select_list(query)

            return data
        except Exception as e:
            print(str(e))
            return False 

    def get_rotation_per_minute(self,current_date):
        try:
            query = (
                "SELECT DATE_TRUNC('minute', timestamp) AS minute_start, "
                "DATE_TRUNC('minute', timestamp) + INTERVAL '1 minute' AS minute_end, "
                "COUNT(rotation) AS rotation_count, "
                "TO_CHAR(DATE_TRUNC('minute', timestamp), 'YYYY-MM-DD') AS day "
                "FROM rotation_details "
                "WHERE timestamp >= '" + str(current_date) + "' "
                "AND timestamp < '" + str(current_date) + "'::timestamp + INTERVAL '1 day' "
                "GROUP BY minute_start, minute_end, day "
                "ORDER BY day, minute_start;"
            )
            data = self.execute.select_list(query)

            return data
        except Exception as e:
            print(str(e))
            return False
        
    def sql_query1(self,date):
        try:
            sql_query1 = (
                "SELECT "
                "timestamp "
                "FROM "
                "uptime_status "
                "WHERE "
                "DATE(timestamp) = '" + str(date) + "' "
                "GROUP BY "
                "timestamp "
                "HAVING "
                "COUNT(CASE WHEN software_status = '0' THEN 1 ELSE NULL END) = 1;"
            )
            data = self.execute.select_list(sql_query1)

            return data
        except Exception as e:
            print(str(e))
            return False
        
    def sql_query2(self,date):
        try:
            sql_query2 = (
                "SELECT "
                "timestamp "
                "FROM "
                "uptime_status "
                "WHERE "
                "DATE(timestamp) = '" + str(date) + "' "
                "GROUP BY "
                "timestamp "
                "HAVING "
                "COUNT(CASE WHEN camera_status = '0' THEN 1 ELSE NULL END) = 1;"
            )
            data = self.execute.select_list(sql_query2)

            return data
        except Exception as e:
            print(str(e))
            return False

    def sql_query3(self,date):
        try:
            sql_query3 = (
                "SELECT "
                "timestamp "
                "FROM "
                "uptime_status "
                "WHERE "
                "DATE(timestamp) = '" + str(date) + "' "
                "GROUP BY "
                "timestamp "
                "HAVING "
                "COUNT(CASE WHEN controller_status = '0' THEN 1 ELSE NULL END) = 1;"
            )
            data = self.execute.select_list(sql_query3)

            return data
        except Exception as e:
            print(str(e))
            return False
        
    def sql_query4(self,date):
        try:
            sql_query4 = (
                "SELECT "
                "timestamp "
                "FROM "
                "uptime_status "
                "WHERE "
                "DATE(timestamp) = '" + str(date) + "' "
                "GROUP BY "
                "timestamp "
                "HAVING "
                "COUNT(CASE WHEN image_status = '0' THEN 1 ELSE NULL END) = 1;"
            )
            data = self.execute.select_list(sql_query4)

            return data
        except Exception as e:
            print(str(e))
            return False
        
    def sql_query5(self,date):
        try:
            sql_query5 = (
                "SELECT "
                "timestamp "
                "FROM "
                "uptime_status "
                "WHERE "
                "DATE(timestamp) = '" + str(date) + "' "
                "GROUP BY "
                "timestamp "
                "HAVING "
                "COUNT(CASE WHEN machine_status = '0' THEN 1 ELSE NULL END) > 0;"
            )
            data = self.execute.select_list(sql_query5)

            return data
        except Exception as e:
            print(str(e))
            return False
        
    def sql_query6(self,date):
        try:
            sql_query6 = (
                "SELECT "
                "timestamp "
                "FROM "
                "uptime_status "
                "WHERE "
                "DATE(timestamp) = '" + str(date) + "' "
                "GROUP BY "
                "timestamp "
                "HAVING "
                "COUNT(CASE WHEN machine_status = '1' AND image_status = '0' THEN 1 ELSE NULL END) > 0;"
            )
            data = self.execute.select_list(sql_query6)

            return data
        except Exception as e:
            print(str(e))
            return False





if __name__ == "__main__":
    report = DayReportDb()
    print(report.sql_query6("2024-02-27"))
