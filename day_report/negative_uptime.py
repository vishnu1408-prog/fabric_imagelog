from src.config import Config
import matplotlib.pyplot as plt
import os,sys,re,datetime,traceback
from datetime import date,timedelta
from day_report.db import DayReportDb
from matplotlib.backends.backend_pdf import PdfPages


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

config = Config()
day_report_db = DayReportDb()


class NegetiveUptime:
    def __init__(self):
        self.log_file_path =  "./system_stats.log"

    def log(self,today):
        try:
            data_entries = []
            timestamps = []
            pattern = r"\x00\\"
            try:
                with open(self.log_file_path, "r") as file:
                    for line in file:
                        if bool(re.search(pattern, line)) or "\\00\\00" in str(line) or "\\" in str(line):
                            continue

                        parts = line.split(",")
                        if len(parts) >= 6:
                            try:
                                entry = {
                                    "timestamp"             :       parts[0],
                                    "cpu_utilization"       :       float(parts[1].split(": ")[1].rstrip("%")),
                                    "ram_usage"             :       int(parts[2].split(": ")[1].split(" ")[0]),
                                    "machine_status"        :       int(parts[3].split(": ")[1]),
                                    "gpu_utilization"       :       float(parts[4].split(": ")[1].rstrip("%")),
                                    "memory_utilization"    :       float(parts[5].split(": ")[1].rstrip("%")),
                                    "temperature"           :       int(parts[6].split(": ")[1]),
                                }
                                timestamp = datetime.datetime.strptime(
                                    parts[0], "%Y-%m-%d %H:%M:%S.%f"
                                )

                                if timestamp.date() == datetime.datetime.strptime(today , "%Y-%m-%d").date():

                                    timestamps.append(timestamp)
                                    data_entries.append(entry)
                            except:
                                print(f"error processing this line {str(line)}")
                        else:
                            print(f"Skipping line: {line}")

            except FileNotFoundError as e:
                print(f"File not found: {self.log_file_path}")

            return data_entries, timestamps
        except Exception as e:
            print(str(e))
            return False

    def postgre(self,user_date):
        try:
            timestamps = []
            # Read the log file
            with open("./system_stats.log", "r") as file:
                for line in file:
                    if user_date in line and "PostgreSQL: Not Running" in line:
                        # Extract the timestamp from the line and convert it to a datetime object
                        timestamp_str = line.split()[1]
                        timestamp = datetime.datetime.strptime(
                            timestamp_str, "%H:%M:%S.%f:"
                        )
                        timestamps.append(timestamp)
            return timestamps
        except Exception as e:
            print(str(e))
            return False

    def docker(self,user_date):
        try:
            timestamps = []
            # Read the log file
            with open("./system_stats.log", "r") as file:
                for line in file:
                    if user_date in line and "Docker_ml: Not Running" in line:
                        # Extract the timestamp from the line and convert it to a datetime object
                        timestamp_str = line.split()[1]
                        timestamp = datetime.datetime.strptime(
                            timestamp_str, "%H:%M:%S.%f:"
                        )
                        timestamps.append(timestamp)
            return timestamps
        except Exception as e:
            print(str(e))
            return False

    def docker_alarm(self,user_date):
        try:
            timestamps = []
            # Read the log file
            with open("./system_stats.log", "r") as file:
                for line in file:
                    if user_date in line and "Docker_alarm: Not Running" in line:
                        # Extract the timestamp from the line and convert it to a datetime object
                        timestamp_str = line.split()[1]
                        timestamp = datetime.datetime.strptime(
                            timestamp_str, "%H:%M:%S.%f:"
                        )
                        timestamps.append(timestamp)
            return timestamps
        except Exception as e:
            print(str(e))
            return False

    def generate_plot(
        self,
        user_date,
        missing_minutes_per_hour,
        data_entries,
        timestamp,
        timestamp_db,
        timestamp_docker,
        timestamp_alarm,
        pdf_pages,
    ):
        try:
            print("Code is running, it will take time")
            # path = "/home/kniti"
            # stat = shutil.disk_usage(path)
            # free_space_gb = stat.free / 1e9
            all_minutes_within_hour_log = []  # Accumulate all minutes data

            for hour_key, missing_minutes in missing_minutes_per_hour.items():
                # Extract the datetime objects from missing_minutes
                missing_minutes_datetime = missing_minutes

                # Create corresponding datetimes with the same date and hour
                datetimes = [
                    minute.replace(second=0, microsecond=0)
                    for minute in missing_minutes_datetime
                ]

                # Convert datetimes to minutes within the hour
                minutes_within_hour_log = [t.hour * 60 + t.minute for t in datetimes]

                # Append the minutes data to the accumulated list
                all_minutes_within_hour_log.extend(minutes_within_hour_log)

            minute_counts = {}
            for minute in all_minutes_within_hour_log:
                if minute in minute_counts:
                    minute_counts[minute] += 1
                else:
                    minute_counts[minute] = 1

            # Extract minutes and corresponding counts
            minutes = list(minute_counts.keys())
            counts = [
                1 if minute_counts[minute] > 1 else minute_counts[minute]
                for minute in minutes
            ]

 
            timestamps_log = timestamp
            timestamp_gre = timestamp_db
            timestamp_dck = timestamp_docker
            timestamp_alm = timestamp_alarm
            target_date = user_date


            

            
            timestamps_software     =   day_report_db.sql_query1(target_date)
  
            timestamps_camera       =   day_report_db.sql_query2(target_date)
  
            timestamps_controller   =   day_report_db.sql_query3(target_date)
  
            timestamps_image        =   day_report_db.sql_query4(target_date)
  
            timestamps_machine      =   day_report_db.sql_query5(target_date)
  
            timestamps_image2       =   day_report_db.sql_query6(target_date)


            minutes_within_hour_log = [t.hour * 60 + t.minute for t in timestamps_log]
            minutes_within_hour_machineOff = [
                [num for num in range(1440) if num not in minutes_within_hour_log]
            ]
            if str(date.today()) == user_date:
                end_minute = (
                    0
                    if len(minutes_within_hour_log) == 1
                    else minutes_within_hour_log[len(minutes_within_hour_log) - 1]
                )
                minutes_within_hour_machineOff = [
                    [num for num in range(end_minute) if num not in minutes_within_hour_log]
                ]
            minutes_within_hour_software = [
                timestamp[0].hour * 60 + timestamp[0].minute
                for timestamp in timestamps_software
            ]
            minutes_within_hour_camera = [
                timestamp[0].hour * 60 + timestamp[0].minute
                for timestamp in timestamps_camera
            ]
            minutes_within_hour_controller = [
                timestamp[0].hour * 60 + timestamp[0].minute
                for timestamp in timestamps_controller
            ]
            minutes_within_hour_image = [
                timestamp[0].hour * 60 + timestamp[0].minute
                for timestamp in timestamps_image
            ]
            minutes_within_hour_machine = [
                timestamp[0].hour * 60 + timestamp[0].minute
                for timestamp in timestamps_machine
            ]
            minutes_within_hour_db = [t.hour * 60 + t.minute for t in timestamp_gre]
            minutes_within_hour_image2 = [
                timestamp[0].hour * 60 + timestamp[0].minute
                for timestamp in timestamps_image2
            ]
            minutes_within_hour_docker = [t.hour * 60 + t.minute for t in timestamp_dck]
            minutes_within_hour_alarm = [t.hour * 60 + t.minute for t in timestamp_alm]

            bar_width = 0.1  # Adjust this value as needed

            # Create subplots with shared x-axis
            fig, (ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8,ax9,ax10,ax11,ax12,ax13,ax14,ax15,) = plt.subplots(15, 1, figsize=(40, 40), sharex=True)

            # Plot the first query result in the lower subplot
            ax1.bar(
                minutes_within_hour_log,
                [1] * len(minutes_within_hour_log),
                width=bar_width,
                align="center",
                color="green",
            )
            ax2.bar(
                minutes_within_hour_machineOff[0],
                [1] * len(minutes_within_hour_machineOff[0]),
                width=0.1,
                align="center",
                color="red",
            )
            ax3.bar(
                minutes_within_hour_software,
                [1] * len(minutes_within_hour_software),
                width=bar_width,
                align="edge",
                color="red",
            )
            ax3.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax4.bar(
                minutes_within_hour_camera,
                [1] * len(minutes_within_hour_camera),
                width=bar_width,
                align="edge",
                color="red",
            )
            ax4.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax5.bar(
                minutes_within_hour_controller,
                [1] * len(minutes_within_hour_controller),
                width=bar_width,
                align="edge",
                color="red",
            )
            ax5.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax6.bar(
                minutes_within_hour_image,
                [1] * len(minutes_within_hour_image),
                width=bar_width,
                align="edge",
                color="red",
            )
            ax6.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax7.bar(
                minutes_within_hour_image2,
                [1] * len(minutes_within_hour_image2),
                width=bar_width,
                align="edge",
                color="red",
            )
            ax7.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax8.bar(
                minutes_within_hour_machine,
                [1] * len(minutes_within_hour_machine),
                width=bar_width,
                align="edge",
                color="red",
            )
            ax8.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax9.bar(
                minutes_within_hour_db,
                [1] * len(minutes_within_hour_db),
                width=bar_width,
                align="center",
                color="red",
            )
            ax9.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax10.bar(
                minutes_within_hour_docker,
                [1] * len(minutes_within_hour_docker),
                width=bar_width,
                align="center",
                color="red",
            )
            ax10.bar(minutes, counts, width=0.1, align="center", color="blue")
            ax11.bar(
                minutes_within_hour_alarm,
                [1] * len(minutes_within_hour_alarm),
                width=bar_width,
                align="center",
                color="red",
            )
            ax11.bar(minutes, counts, width=0.1, align="center", color="blue")

            # Plot additional system statistics

            ax12.plot(
                minutes_within_hour_log,
                [entry["cpu_utilization"] for entry in data_entries],
                label="CPU Utilization",
                color="purple",
                linewidth=0.1,
            )
            ax13.plot(
                minutes_within_hour_log,
                [entry["gpu_utilization"] for entry in data_entries],
                label="GPU Utilization",
                color="orange",
                linewidth=0.3,
            )
            ax14.plot(
                minutes_within_hour_log,
                [entry["memory_utilization"] for entry in data_entries],
                label="Memory Usage",
                color="cyan",
                linewidth=0.7,
            )
            ax15.plot(
                minutes_within_hour_log,
                [entry["temperature"] for entry in data_entries],
                label="Temperature",
                color="red",
                linewidth=0.5,
            )
            name = config.get("report", "millname")
            machinName = day_report_db.get_machine_name()
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
            ax1.set_title(
                f"{name}_{machinName}_NEGATIVE_UPTIME_FOR-{user_date}", fontsize=24
            )
            ax11.set_xlabel(f"Free space : {0} gb", fontsize=24, loc="right")
            ax1.set_title(
                f"Pdf generated at : {formatted_datetime}", fontsize=24, loc="right"
            )
            ax1.set_title(
                f"Pdf generated at : {formatted_datetime}", fontsize=24, loc="right"
            )
            ax1.set_title(
                f'Version : {config.get("report","version")}', fontsize=24, loc="left"
            )
            # plt.xticks(range(0, 1440, 60), [f'{i // 60:02}:{i % 60:02}' for i in range(0, 1440, 60)])
            plt.xticks(
                range(0, 1440, 120),
                [f"{i // 60:02}:{i % 60:02}" for i in range(0, 1440, 120)],
            )

            legend1  =  ax1 . legend(["Knit-i on  Status"], loc="upper left", fontsize="25")
            legend2  =  ax2 . legend(["Knit-i off Status"], loc="upper left", fontsize="25")
            legend3  =  ax3 . legend(["Software off Status"], loc="upper left", fontsize="25")
            legend4  =  ax4 . legend(["Camera off Status"], loc="upper left", fontsize="25")
            legend5  =  ax5 . legend(["Controller off Status"], loc="upper left", fontsize="25")
            legend6  =  ax6 . legend(["Image off status"], loc="upper left", fontsize="25")
            legend7  =  ax7 . legend(["Machine On Image off Status"], loc="upper left", fontsize="25")
            legend8  =  ax8 . legend(["Machine off Status"], loc="upper left", fontsize="25")
            legend9  =  ax9 . legend(["Db off status"], loc="upper left", fontsize="25")
            legend10 =  ax10. legend(["Docker-ML off status"], loc="upper left", fontsize="25")
            legend11 =  ax11. legend(["Docker-alarm off status"], loc="upper left", fontsize="25")
            legend12 =  ax12. legend(["Cpu Utilization"], loc="upper left", fontsize="25")
            legend13 =  ax13. legend(["GPU Utilization"], loc="upper left", fontsize="25")
            legend14 =  ax14. legend(["Memory Utilization"], loc="upper left", fontsize="25")
            legend15 =  ax15. legend(["Temperature"], loc="upper left", fontsize="25")

            ax12.set_ylim(0, 100)
            ax13.set_ylim(0, 100)
            ax14.set_ylim(0, 100)

            ax1.add_artist(legend1)
            ax2.add_artist(legend2)
            ax3.add_artist(legend3)
            ax4.add_artist(legend4)
            ax5.add_artist(legend5)
            ax6.add_artist(legend6)
            ax7.add_artist(legend7)
            ax8.add_artist(legend8)
            ax9.add_artist(legend9)
            ax10.add_artist(legend10)
            ax11.add_artist(legend11)
            ax12.add_artist(legend12)
            ax13.add_artist(legend13)
            ax14.add_artist(legend14)
            ax15.add_artist(legend15)

            plt.tight_layout()
            pdf_pages.savefig()
            plt.close()

            print(f"Uptime report generated for {user_date}")
        except Exception as e:
            print(str(e))
            return False

    def create_directory(self,today):
            filePath = config.get("path", "negative_uptime")
            machinName = day_report_db.get_machine_name()
            millName = config.get("report", "millname")
            PdfName = f"{millName}_{machinName}_Uptime_{today}.pdf"
            directory = f"{filePath}/{PdfName}"
            os.makedirs(filePath, exist_ok=True)

            for filename in os.listdir(filePath):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(filePath, filename)
                    os.remove(file_path)
            
            return directory

    def uptime(self,user_input_date):
        try:
            pdf_file = self.create_directory(user_input_date)

            pdf_pages = PdfPages(pdf_file)

            filtered_data_entries , filtered_timestamps = self.log(user_input_date)

            

            if len(filtered_data_entries) == 0:
                filtered_data_entries.append(
                    {
                        "timestamp": 0,
                        "cpu_utilization": 0,
                        "ram_usage": 0,
                        "machine_status": 0,
                        "gpu_utilization": 0,
                        "memory_utilization": 0,
                        "temperature": 0,
                    }
                )
                filtered_timestamps.append(
                    datetime.datetime(2023, 12, 20, 11, 8, 2, 660009)
                )
            missing_minutes_per_hour = {}
            filtered_timestamps.sort()
            first_timestamp = min(filtered_timestamps)
            last_timestamp = max(filtered_timestamps)
            current_hour = datetime.datetime(
                first_timestamp.year, first_timestamp.month, first_timestamp.day
            )
            current_minute = 0  # Initialize current_minute to 0

            while current_hour <= last_timestamp:
                hour_key = current_hour.strftime("%Y-%m-%d %H")

                # Check if the hour is not in filtered_timestamps
                if hour_key not in [
                    ts.strftime("%Y-%m-%d %H") for ts in filtered_timestamps
                ]:
                    # If not in filtered_timestamps, add all 60 minutes for this hour
                    if hour_key not in missing_minutes_per_hour:
                        missing_minutes_per_hour[hour_key] = []

                    for missing_minute in range(current_minute, 60):
                        missing_minutes_per_hour[hour_key].append(
                            current_hour + timedelta(minutes=missing_minute)
                        )
                    current_minute = (
                        0
                    )  # Reset current_minute after adding all missing minutes

                current_hour += timedelta(hours=1)

            if first_timestamp.minute != 0:
                # Calculate the missing minutes before the current time
                missing_minutes_before_current = first_timestamp.minute
                if hour_key not in missing_minutes_per_hour:
                    missing_minutes_per_hour[hour_key] = []
                for missing_minute in range(1, int(missing_minutes_before_current)):
                    missing_minute_timedelta = timedelta(minutes=missing_minute)
                    missing_minute_timestamp = first_timestamp - missing_minute_timedelta
                    missing_minutes_per_hour[hour_key].append(missing_minute_timestamp)

            for i in range(len(filtered_timestamps) - 1):
                current_time = filtered_timestamps[i]
                next_time = filtered_timestamps[i + 1]
                time_diff = (next_time - current_time).total_seconds() / 60
                if time_diff > 1:
                    hour_key = current_time.strftime("%Y-%m-%d %H:00:00")
                    if hour_key not in missing_minutes_per_hour:
                        missing_minutes_per_hour[hour_key] = []
                    for missing_minute in range(1, int(time_diff)):
                        missing_minutes_per_hour[hour_key].append(
                            current_time + timedelta(minutes=missing_minute)
                        )

            timestamp_db = self.postgre(user_input_date)
            timestamp_docker = self.docker(user_input_date)
            timestamp_alarm = self.docker_alarm(user_input_date)
            with pdf_pages:
                self.generate_plot(
                    user_input_date,
                    missing_minutes_per_hour,
                    filtered_data_entries,
                    filtered_timestamps,
                    timestamp_db,
                    timestamp_docker,
                    timestamp_alarm,
                    pdf_pages,
                )
        except Exception as e:
            print(str(e))
            return False

    def get_disk_space(self):
        try:
            url = "http://127.0.0.1:8002/space/"
            import requests
            import json

            data = json.dumps({f"date": "2023-12-21"})
            r = requests.post(url, json={"name": "temp", "data": data})
            space = "Monitor Service is Off"
            try:
                space = str(r.json()["space"])
            except Exception as e:
                print(str(e))
            return space
        except Exception as e:
            print(str(e))
            return False

class GreenCamUptime:
    def __init__(self):
        self.green_cam_1 = "./green_cam/greencam1_uptime.log"
        self.green_cam_2 = "./green_cam/greencam2_uptime.log"

    def create_directory(self,today):
        filePath = config.get("path", "green_cam")
        machinName = day_report_db.get_machine_name()
        millName = config.get("report", "millname")
        PdfName = f"{millName}_{machinName}_GreenCam_Uptime_{today}.pdf"
        directory = f"{filePath}/{PdfName}"
        os.makedirs(filePath, exist_ok=True)

        for filename in os.listdir(filePath):
            if filename.endswith(".pdf"):
                file_path = os.path.join(filePath, filename)
                os.remove(file_path)
        
        return directory

    def get_missing_minutes(self,data_var_house):
        try:

            for i in range(0, 1440):
                if i not in data_var_house:
                    data_var_house[i] = {
                        "cam_on_status"       : 0,
                        "cpu_utilization"     : 0,
                        "temperature"         : 0,
                        "memory_utilization"  : 0,
                        "fps"                 : 0,
                    }
            return dict(sorted(data_var_house.items()))
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            return False    

    def data_collector(self,date,file_path):
        try:
            data_var_house = {}
            with open(file_path, "r") as file:
                for line in file:
                    if date in line:
                        # Define the regex pattern
                        pattern = r"TIMESTAMP: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6},STATUS: \d,CPU_UTILIZATION: \d{1,3}\.\d+,TEMPERATURE: \d{1,3}\.\d+,MEMORY_UTILIZATION: \d{1,3}\.\d,FPS: \d{1,3}"
                        # Check if the line matches the pattern
                        if re.match(pattern, line):
                            parts = line.split(",")
                            timestamp = parts[0].split(":", 1)[1].strip()
                            # Convert the timestamp string into a datetime object
                            timestamp_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                            if timestamp_obj.date() == datetime.datetime.strptime(date, "%Y-%m-%d").date():
                                minutes = timestamp_obj.hour * 60 + timestamp_obj.minute
                                cam_on_status_val       =  int( parts[1].split(":")[1] )
                                cpu_utilization_val     =  int( float(parts[2].split(":")[1]) )
                                temperature_val         =  int( float(parts[3].split(":")[1]) )
                                memory_utilization_val  =  int( float(parts[4].split(":")[1]) )
                                fps_val                 =  int( parts[5].split(":")[1] )
                                data_var_house[minutes] = {
                                    "cam_on_status"       : cam_on_status_val,
                                    "cpu_utilization"     : cpu_utilization_val,
                                    "temperature"         : temperature_val,
                                    "memory_utilization"  : memory_utilization_val,
                                    "fps"                 : fps_val,
                                }
                            
                        else:
                            print(f"Patten Not matched: {line}")

            return self.get_missing_minutes(data_var_house)      
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            return False

    def separator(self,data_collector):
        try:
            timestamp = []
            cam_on_status = []
            cpu_utilization = []
            temperature = []
            memory_utilization = []
            fps = []
            for key in data_collector:
                timestamp.append(key)
                cam_on_status.append(data_collector[key]["cam_on_status"])
                cpu_utilization.append(data_collector[key]["cpu_utilization"])
                temperature.append(data_collector[key]["temperature"])
                memory_utilization.append(data_collector[key]["memory_utilization"])
                fps.append(data_collector[key]["fps"])

            return timestamp,cam_on_status,cpu_utilization,temperature,memory_utilization,fps
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            return False

    def plot_graph(self,data_collector1,data_collector2,pdf_pages,date):
        try:
            bar_width = 0.1  # Adjust this value as needed
            colour = "red"   # Adjust this colour bar as needed
            timestamp1,cam_on_status1,cpu_utilization1,temperature1,memory_utilization1,fps1 = self.separator(data_collector1)
            timestamp2,cam_on_status2,cpu_utilization2,temperature2,memory_utilization2,fps2 = self.separator(data_collector2)
            # Create subplots with shared x-axis
            fig, (ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8,ax9,ax10,) = plt.subplots(10, 1, figsize=(40, 40), sharex=True)
            
            # Set the x-axis ticks and labels
            xticks = range(0, 1440, 60)
            xticklabels = [f"{i // 60:02}:{i % 60:02}" for i in xticks]

            for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10]:
                ax.set_xticks(xticks)
                ax.set_xticklabels(xticklabels)
                ax.tick_params(labelbottom=True)

            # Plot the Bar graph
            ax1. bar(timestamp1   ,cam_on_status1      ,  width=bar_width   ,align="center"  , color=colour,)

            ax2. bar(timestamp1   ,fps1                ,  width=bar_width   ,align="center"  , color=colour,)

            ax3.plot(timestamp1, cpu_utilization1, color=colour)

            ax4.plot(timestamp1, temperature1, color=colour)

            ax5.plot(timestamp1, memory_utilization1, color=colour)

            ax6. bar(timestamp2   ,cam_on_status2      ,  width=bar_width   ,align="edge"    , color=colour,)

            ax7. bar(timestamp2   ,fps2                ,  width=bar_width   ,align="edge"    , color=colour,)

            ax8.plot(timestamp2, cpu_utilization2, color=colour)

            ax9.plot(timestamp2, temperature2, color=colour)

            ax10.plot(timestamp2, memory_utilization2, color=colour)


            # Set the x-axis label
            legend1  =  ax1 . legend(["Cam1 On Status"          ], loc="upper left", fontsize="25")
            legend2  =  ax2 . legend(["Cam1 FPS"                ], loc="upper left", fontsize="25")
            legend3  =  ax3 . legend(["Cam1 CPU Utilization"    ], loc="upper left", fontsize="25")
            legend4  =  ax4 . legend(["Cam1 Temparature"        ], loc="upper left", fontsize="25")
            legend5  =  ax5 . legend(["Cam1 Memory Utilization" ], loc="upper left", fontsize="25")
            
            legend6  =  ax6 . legend( ["Cam2 On Status"          ], loc="upper left", fontsize="25")
            legend7  =  ax7 . legend( ["Cam2 FPS"                ], loc="upper left", fontsize="25")
            legend8  =  ax8 . legend( ["Cam2 CPU Utilization"    ], loc="upper left", fontsize="25")
            legend9  =  ax9 . legend( ["Cam2 Temparature"        ], loc="upper left", fontsize="25")
            legend10 =  ax10. legend( ["Cam2 Memory Utilization" ], loc="upper left", fontsize="25")
            
            # Add the legends to the subplots
            ax1.  add_artist(legend1)
            ax2.  add_artist(legend2)
            ax3.  add_artist(legend3)
            ax4.  add_artist(legend4)
            ax5.  add_artist(legend5)
            ax6.  add_artist(legend6)
            ax7.  add_artist(legend7)
            ax8.  add_artist(legend8)
            ax9.  add_artist(legend9)
            ax10.add_artist(legend10)


            name = config.get("report", "millname")
            machinName = day_report_db.get_machine_name()
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

            ax1.set_title(
                f"{name}_{machinName}_GREENCAM_UPTIME_FOR-{date}", fontsize=24
            )
            ax1.set_title(
                f"Pdf generated at : {formatted_datetime}", fontsize=24, loc="right"
            )

            ax1.set_title(
                f'Version : {config.get("report","version")}', fontsize=24, loc="left"
            )
            
            plt.tight_layout()
            pdf_pages.savefig()
            plt.close()
            return True
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            return False

    def generate_green_cam_uptime(self,date):
        try:
            pdf_file = self.create_directory(date)
            pdf_pages = PdfPages(pdf_file)
            #data collection
            data_collector1 = self.data_collector(date,self.green_cam_1)
            data_collector2 = self.data_collector(date,self.green_cam_2)

            with pdf_pages:
                self.plot_graph(data_collector1,data_collector2,pdf_pages,date)


        except Exception as e:
            print(str(e))
            traceback.print_exc()
            return False
    

if __name__ == "__main__":
    nagetive_uptime = NegetiveUptime()
    nagetive_uptime.log("2024-01-24")