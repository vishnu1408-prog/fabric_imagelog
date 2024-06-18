import pandas as pd
from io import BytesIO
import os,datetime,traceback
from src.config import Config
from datetime import timedelta
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
from day_report.db import DayReportDb
from matplotlib.backends.backend_pdf import PdfPages

config = Config()
day_report_db = DayReportDb()


class Performance:
    def __init__(self):
        self.logo_path = "assets/logo2.png"

    def roundToNearestMultipleOf3(self ,x):
        try:
            rounded_value = int(3 * round(float(x) / 3))
            if rounded_value <= 30:
                return rounded_value
            else:
                return 30
        except Exception as e:
            print(str(e))
            return False

    def place_log(self,fig,logo_img):
        try:
            ax_logo = fig.add_subplot(1, 1, 1)
            # Adjust the logo's position (move it up or down)
            logo_y_position = 0.87  # Adjust this value (0.7 is the default)
            ax_logo.set_position(
                [0.68, logo_y_position, 0.2, 0.2]
            )  # [left, bottom, width, height]
            # Adjust the logo's size
            logo_width = 0.2  # Adjust this value (0.2 is the default)
            ax_logo.imshow(
                logo_img,
                extent=[
                    0,
                    logo_width,
                    0,
                    logo_width * logo_img.shape[0] / logo_img.shape[1],
                ],
            )
            # Turn off axis for the logo subplot
            ax_logo.axis("off")
            ax_logo.set_frame_on(False)
            return True
                    
        except Exception as e:
            # Getting the stack trace as a string
            error_traceback = traceback.format_exc()
            # Now you can log the error and traceback to a file or elsewhere
            print(f"Error occurred: {e}\nTraceback: {error_traceback}")
            return False       

    def production_bar_graph(self,ax1,current_date):
        try:
            data1 = day_report_db.get_rotation_per_hour(current_date)
            print("ax1",len(data1))
            dates1 = [row[0] for row in data1]
            hours1 = [row[1] for row in data1]
            rotation_counts1 = [row[2] for row in data1]
            daily_rotation_counts = {}
            for date, count in zip(dates1, rotation_counts1):
                if date not in daily_rotation_counts:
                    daily_rotation_counts[date] = count
                else:
                    daily_rotation_counts[date] += count
            ax1.bar(hours1, rotation_counts1, label="Rotation Count", color="red")
            ax1.set_xlabel("Time of the Day(HOUR)", fontsize=18)
            ax1.set_ylabel("Rotation Count", fontsize=18)
            ax1.set_title("PRODUCTION REPORT", fontsize=24, y=1.03)
            ax1.set_xticks(range(24))
            ax1.legend()
            text_x = 0.85

            name = config.get("report", "millname")
            
            machinename = day_report_db.get_machine_name()
            version = config.get("report", "version")
            if len(rotation_counts1)!=0:
                text_y = max(rotation_counts1) + 600
                text_z = max(rotation_counts1) + 750  # Adjust the y-coordinate as needed
                ax1.text(
                    text_x,
                    text_y,
                    f"{name} {machinename} ProductionReport for Date: {current_date}",
                    fontsize=24,
                    color="black",
                )
                ax1.text(text_x, text_z, f"Version : {version}", fontsize=24, color="black")
                for i, count in enumerate(rotation_counts1):
                    ax1.annotate(
                        str(count),
                        xy=(hours1[i], count),
                        xytext=(hours1[i], count + 10),
                        ha="center",
                        va="bottom",
                        fontsize=15,
                        color="black",
                    )
            return daily_rotation_counts
                    
        except Exception as e:
            # Getting the stack trace as a string
            error_traceback = traceback.format_exc()
            # Now you can log the error and traceback to a file or elsewhere
            print(f"Error occurred: {e}\nTraceback: {error_traceback}")
            return False

    def defect_report_bar_graph(self,ax2,current_date):
        try:
            data6 = day_report_db.get_timestamp_defect_type(current_date)
            print("ax2",len(data6))
            hours   = []
            counts  = []
            defect_log_table_data = []
            defect_log_df = pd.DataFrame(data6, columns=["timestamp", "defect_type"])
            if len(data6)!=0:
                defect_log_df["date"] = defect_log_df["timestamp"].dt.date
                defect_log_df["time"] = defect_log_df["timestamp"].dt.strftime(
                    "%H:%M:%S"
                )  # Format the time as HH:MM:SS
                defect_log_df.drop(columns=["timestamp"], inplace=True)

                for sno, row in enumerate(defect_log_df.iterrows(), start=1):
                    defect_log_table_data.append(
                        [sno, row[1]["time"], row[1]["defect_type"]]
                    )

                hour_counts = Counter(
                    item[1].split(":")[0] for item in defect_log_table_data
                )
                hours = [
                    str(i).zfill(2) for i in range(24)
                ]  # Generate a list of all 24 hours as strings
                counts = [hour_counts[hour] for hour in hours]

            bars = ax2.bar(hours, counts)
            ax2.set_xlabel("Time of the Day(Hour)", fontsize=18)
            ax2.set_ylabel("Defect Count", fontsize=18)
            ax2.set_title("DEFECT REPORT", fontsize=24, y=1.03)
            ax2.set_xticks(hours)
            # add the counts on top of each bar
            for bar, count in zip(bars, counts):
                    if count != 0:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width() / 2, height, str(count), ha='center', va='bottom')

            return defect_log_table_data,False,defect_log_df
            
                    
        except Exception as e:
            # Getting the stack trace as a string
            error_traceback = traceback.format_exc()
            # Now you can log the error and traceback to a file or elsewhere
            print(f"Error occurred: {e}\nTraceback: {error_traceback}")
            return False

    def defect_count_bar_graph(self,ax3,defect_log_table_data,flag):
        try:
            defect_type_counts = Counter(item[2] for item in defect_log_table_data)
            print("ax3",len(defect_type_counts))
            defect_types = list(defect_type_counts.keys())
            defect_counts = list(defect_type_counts.values())
            bars = ax3.bar(defect_types, defect_counts)
            ax3.set_xlabel("Defect Type", fontsize=18)
            ax3.set_ylabel("Defect Count", fontsize=18)
            ax3.set_title("DEFECT COUNT BY TYPE", fontsize=24)
            # add the counts on top of each bar
            for bar, count in zip(bars, defect_counts):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width() / 2, height, str(count), ha='center', va='bottom')

            return True
                    
        except Exception as e:
            # Getting the stack trace as a string
            error_traceback = traceback.format_exc()
            # Now you can log the error and traceback to a file or elsewhere
            print(f"Error occurred: {e}\nTraceback: {error_traceback}")
            return False

    def create_roll_details_table(self,current_date,defect_log_df, daily_rotation_counts,logo_img,pdf_pages):
        try:
            fig, ax5 = plt.subplots(figsize=(21, 10))
            ax_logo = fig.add_subplot(1, 1, 1)
            ax_logo.imshow(logo_img)
            ax_logo.axis("off")
            logo_y_position = 0.83  # Adjust this value (0.7 is the default)   
            ax_logo.set_position(
                [0.68, logo_y_position, 0.2, 0.2]
            )  # [left, bottom, width, height]
            # Adjust the logo's size
            logo_width = 0.2  # Adjust this value (0.2 is the default)
            ax_logo.imshow(
                logo_img,
                extent=[
                    0,
                    logo_width,
                    0,
                    logo_width * logo_img.shape[0] / logo_img.shape[1],
                ],
            )
            # Turn off axis for the logo subplot
            ax_logo.axis("off")
            ax_logo.set_frame_on(False)
            ax5.set_title(f"Roll Details", fontsize=24)
            ax5.axis("tight")
            ax5.axis("off")


            data = day_report_db.get_roll_details_records(current_date)
            if len(data)!=0:
                roll_details_cellText = [
                    [
                        str(row[0]),
                        str(row[1]),
                        row[2],
                        "null" if row[3] is None else str(row[3]),
                        str(row[4]),
                        str(row[5]),
                    ]
                    for row in data
                ]

                roll_details_df = pd.DataFrame(
                    roll_details_cellText,
                    columns=[
                        "Roll Number",
                        "Roll Start Date",
                        "Roll Start Time",
                        "Order No",
                        "Roll Name",
                        "Revolution",
                    ],
                )

                # Calculate Roll End Time based on the next row's Roll Start Time
                roll_details_df["Roll End Time"] = roll_details_df["Roll Start Time"].shift(
                    -1
                )

                # Set the "Roll End Time" to the end of the day for the last row
                last_row_index = len(roll_details_df) - 1
                if last_row_index >= 0:
                    roll_details_df.at[
                        last_row_index, "Roll End Time"
                    ] = "23:59:59"  # Set to the end of the day

                # Drop the last row as it doesn't have a corresponding next row
                roll_details_df = roll_details_df.dropna(
                    subset=["Roll Start Time", "Roll End Time"]
                )

                roll_details_df["Roll Start Date"] = pd.to_datetime(
                    roll_details_df["Roll Start Date"]
                )  # Convert 'Roll Start Date' to datetime
                roll_details_df["Roll End Date"] = roll_details_df[
                    "Roll Start Date"
                ]  # Initialize 'Roll End Date' to 'Roll Start Date'

                for index in range(len(roll_details_df) - 1):
                    current_row = roll_details_df.iloc[index]
                    next_row = roll_details_df.iloc[index + 1]

                    # Check if the current roll ends on a different date than it starts
                    if current_row["Roll Start Time"] > next_row["Roll Start Time"]:
                        roll_details_df.at[index, "Roll End Date"] = current_row[
                            "Roll Start Date"
                        ] + timedelta(days=1)

                # For the last row, if it's the last entry of the day, set 'Roll End Date' to NaN
                last_row_index = len(roll_details_df) - 1
                if last_row_index >= 0:
                    if (
                        roll_details_df.iloc[last_row_index]["Roll Start Time"]
                        <= "23:59:59"
                    ):
                        roll_details_df.at[
                            last_row_index, "Roll End Date"
                        ] = pd.NaT  # Set to NaN

                # Format 'Roll End Date' as a string, excluding the last row if it's NaN
                roll_details_df["Roll Start Date"] = roll_details_df[
                    "Roll Start Date"
                ].dt.strftime("%Y-%m-%d")
                roll_details_df["Roll End Date"] = roll_details_df[
                    "Roll End Date"
                ].dt.strftime("%Y-%m-%d")

                first_row_index = 0
                roll_details_df["Roll Start Time"] = pd.to_datetime(
                    roll_details_df["Roll Start Time"],
                    format="%H:%M:%S.",
                    errors="coerce",
                    exact=False,
                    infer_datetime_format=True,
                )
                roll_details_df["Roll End Time"] = pd.to_datetime(
                    roll_details_df["Roll End Time"],
                    format="%H:%M:%S",
                    errors="coerce",
                    exact=False,
                    infer_datetime_format=True,
                )
                roll_details_df["Roll Start Time"] = roll_details_df[
                    "Roll Start Time"
                ].dt.strftime("%H:%M:%S")
                roll_details_df["Roll End Time"] = roll_details_df[
                    "Roll End Time"
                ].dt.strftime("%H:%M:%S")

                # Calculate and assign 'Time Taken' for the first row
                start = pd.to_datetime(
                    roll_details_df.at[first_row_index, "Roll Start Time"]
                )
                end = pd.to_datetime(
                    roll_details_df.at[first_row_index, "Roll End Time"]
                ) - timedelta(days=1)
                diff = end - start
                hours = int(diff.seconds // 3600)
                minutes = int((diff.seconds // 60) % 60)
                roll_details_df.at[
                    first_row_index, "Time Taken"
                ] = f"{hours} hr {minutes} min"

                # Calculate and assign 'Time Taken' for other rows
                for row_index in range(1, len(roll_details_df) - 1):
                    time_taken_minutes = (
                        pd.to_datetime(roll_details_df.at[row_index, "Roll End Time"])
                        - pd.to_datetime(roll_details_df.at[row_index, "Roll Start Time"])
                    ).total_seconds() / 60
                    hours = int(time_taken_minutes // 60)
                    minutes = int(time_taken_minutes % 60)
                    roll_details_df.at[
                        row_index, "Time Taken"
                    ] = f"{hours} hr {minutes} min"

                defect_counts = []

                # Start with the beginning of the day for the first row
                start_time = "00:00:00"

                for index, row in roll_details_df.iterrows():
                    roll_start_time = pd.Timestamp(row["Roll Start Time"])

                    # Determine the end_time for the current roll entry
                    if index < len(roll_details_df) - 1:
                        Roll_End_Time = pd.Timestamp(
                            roll_details_df.at[index + 1, "Roll Start Time"]
                        )
                    else:
                        # For the last row, end with the end of the day
                        Roll_End_Time = roll_start_time.replace(
                            hour=23, minute=59, second=59
                        )

                    end_time = Roll_End_Time.strftime("%H:%M:%S")

                    defect_count = (
                        {}
                    )  # Use a dictionary to store defect counts for this roll

                    for defect_type in defect_log_df["defect_type"]:
                        defect_count[
                            defect_type
                        ] = 0  # Initialize counts for all defect types

                    for j in range(
                        0, len(defect_log_df)
                    ):  # Iterate through defect log entries
                        log_time = pd.Timestamp(defect_log_df.at[j, "time"])
                        time = log_time.strftime("%H:%M:%S")

                        # If log_time is within the time range, increment the corresponding defect count
                        if start_time <= time <= end_time:
                            defect_type = defect_log_df.at[j, "defect_type"]
                            defect_count[defect_type] += 1

                    defect_counts.append(defect_count)

                    # Set the start_time for the next roll to be the end_time of the current roll
                    start_time = end_time

                # Add defect_counts as a new column to roll_details_df
                roll_details_df["Defect Counts"] = defect_counts
                roll_details_df.fillna("running", inplace=True)

                
                for index, row in roll_details_df.iterrows():
                    defect_count = row["Defect Counts"]
                    formatted_defect_count = ",\n ".join(
                        [
                            f"{defect_type}: {count}"
                            for defect_type, count in defect_count.items()
                        ]
                    )
                    roll_details_df.at[index, "Defect Counts"] = formatted_defect_count

                # Convert the DataFrame to a list
                table_data = roll_details_df.values.tolist()

            else:
                # Example empty data
                table_data = []

                # Calculate the number of columns based on column labels
                num_columns = len([
                    "Roll Number", "Roll Start Date", "Roll Start Time", "Order No",
                    "Roll id ", "Doff Count", "Roll End Time", "Roll End Date",
                    "Time Taken", "Defect Counts"
                ])

                # If table_data is empty, prepare an empty structure for cellText with the correct number of columns
                if not table_data:
                    # Create a list with a single row of empty strings to match the column count
                    empty_row = [["" for _ in range(num_columns)]]
                    table_data = empty_row
            
            singlePage = 6
            
            # Iterate through the list in groups of 6 rows
            for i in range(0, len(table_data), singlePage):
                # Extract a chunk of 6 rows
                chunk = table_data[i:i+singlePage]
                
                # Create the table with adjusted width and height
                table = ax5.table(cellText=chunk , colLabels=['Roll Number','Roll\nStart Date','Roll\nStart Time','Order No','Roll id','Doff Count','Roll\nEnd Time','Roll\nEnd Date','Time\nTaken','Defect\nCounts'], loc='center', bbox=[0, 0, 1, 1])

                # Customize the appearance of the table
                table.auto_set_font_size(False)
                table.set_fontsize(18)

                # Align content in all cells to center
                for key, cell in table._cells.items():
                    cell.get_text().set_horizontalalignment('center')
                    cell.get_text().set_verticalalignment('center')

                # Calculate the center of the page horizontally
                page_center_horizontal = 0.5
                # Check if it's the last iteration
                if i >= len(table_data) - singlePage:
                    # Handle last iteration  # Add text below the table
                    for date, total_count in daily_rotation_counts.items():
                        ax5.text(page_center_horizontal, -0.08 , f"Total Doff Count: {total_count}", fontsize=18, ha="center", transform=ax5.transAxes)

                pdf_pages.savefig(fig)
                plt.close(fig) 
           
            return True
                    
        except Exception as e:
            # Getting the stack trace as a string
            error_traceback = traceback.format_exc()
            # Now you can log the error and traceback to a file or elsewhere
            print(f"Error occurred: {e}\nTraceback: {error_traceback}")
            return False

    def create_defect_log_report(self, page_num, rows_per_page, defect_log_table_data, logo_img):
        start_idx = page_num * rows_per_page
        end_idx = (page_num + 1) * rows_per_page
        defect_log_table_data_page = defect_log_table_data[start_idx:end_idx]

        # Create a new page for each set of data
        fig, ax4 = plt.subplots(figsize=(21, 29.7))
        ax_logo = fig.add_subplot(1, 1, 1)
        ax_logo.imshow(logo_img)
        ax_logo.axis("off")
        logo_y_position = 0.87  # Adjust this value (0.7 is the default)
        ax_logo.set_position(
            [0.68, logo_y_position, 0.2, 0.2]
        )  # [left, bottom, width, height]
        # Adjust the logo's size
        logo_width = 0.2  # Adjust this value (0.2 is the default)
        ax_logo.imshow(
            logo_img,
            extent=[
                0,
                logo_width,
                0,
                logo_width * logo_img.shape[0] / logo_img.shape[1],
            ],
        )
        # Turn off axis for the logo subplot
        ax_logo.axis("off")
        ax_logo.set_frame_on(False)
        ax4.set_title(f"Defect Log Report", fontsize=24)
        ax4.axis("off")

        # Calculate the position and size of the table based on the title size and available space
        title_height = 0.1  # Adjust this value based on the title height
        table_height = min(1.0, len(defect_log_table_data_page) * 0.15)  # Adjust this value based on the desired table height
        table_bottom = (
            1 - title_height - table_height
        )  # Calculate the bottom position of the table
        table = ax4.table(
            cellText=defect_log_table_data_page,
            colLabels=["SNo", "Time", "Defect Type"],
            cellLoc="center",
            loc="center",
            bbox=[0.1, table_bottom, 0.8, table_height],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(20)
        table.auto_set_column_width([5, 5, 5])
        table.scale(1, 2)
        return fig


    def create_rpm_dotted_graph(self,current_date,logo_img):
        rotation_per_minute = day_report_db.get_rotation_per_minute(current_date)
        df = pd.DataFrame(
            rotation_per_minute, columns=["minute_start", "minute_end", "rotation_count", "day"]
        )
        df["rotation_count"] = df["rotation_count"].apply(self.roundToNearestMultipleOf3)
        # Get the unique dates in the DataFrame
        unique_dates = df["day"].unique()
        # Create a dictionary to hold the RPM Count for each minute in an hour for each day
        minute_rpm_counts = {
            date: {hour: {minute: 0 for minute in range(60)} for hour in range(24)}
            for date in unique_dates
        }
        # Populate the RPM Count in the dictionary based on the data in the DataFrame
        for _, row in df.iterrows():
            date = row["day"]
            hour = row["minute_start"].hour
            minute = row["minute_start"].minute
            rpm_count = row["rotation_count"]
            minute_rpm_counts[date][hour][minute] = rpm_count
        # Create lists for plotting
        rpm_counts = [
            minute_rpm_counts[date][hour][minute]
            for date in unique_dates
            for hour in range(24)
            for minute in range(60)
        ]
        # Create a list of datetime objects for the x-axis (for proper formatting)
        datetime_labels = [
            pd.to_datetime(f"{date} {hour:02d}:{minute:02d}")
            for date in unique_dates
            for hour in range(24)
            for minute in range(60)
        ]
        fig, ax = plt.subplots(figsize=(30, 10))
        ax_logo = fig.add_subplot(1, 1, 1)
        ax_logo.imshow(logo_img)
        ax_logo.axis("off")
        logo_y_position = 0.89  # Adjust this value (0.7 is the default)
        ax_logo.set_position(
            [0.68, logo_y_position, 0.1, 0.1]
        )  # [left, bottom, width, height]
        # Adjust the logo's size
        logo_width = 0.2  # Adjust this value (0.2 is the default)
        ax_logo.imshow(
            logo_img,
            extent=[
                0,
                logo_width,
                0,
                logo_width * logo_img.shape[0] / logo_img.shape[1],
            ],
        )
        # Turn off axis for the logo subplot
        ax_logo.axis("off")
        ax_logo.set_frame_on(False)
        ax.plot(
            datetime_labels, rpm_counts, marker="o", linestyle="None", color="blue"
        )
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_xlabel("Time of the day (Hour)")
        ax.set_ylabel("Rotation Per Minute (RPM)")
        ax.set_title(f'RPM Count for {current_date.strftime("%Y-%m-%d")}')
        return fig

    def generate_pdf_plots(self,start_date, end_date):
        try:
            # Convert the date strings to datetime objects
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            # Calculate the number of days in the date range
            num_days = (end_date - start_date).days + 1
            # Create a PDF file to save the plots
            pdf_buffer = BytesIO()
            pdf_pages = PdfPages(pdf_buffer)
            plt.ioff()
            # Iterate over the date range
            logo_img = mpimg.imread(self.logo_path)
            for i in range(num_days):
                # Calculate the current date within the range
                current_date = start_date + datetime.timedelta(days=i)
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(21, 29.7))
                plt.subplots_adjust(hspace=0.8)
# <-------------page one ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------>

                self.place_log(fig,logo_img)
    
                daily_rotation_counts                    =  self.production_bar_graph(ax1,current_date)

                defect_log_table_data,flag,defect_log_df =  self.defect_report_bar_graph(ax2,current_date)
               
                self.defect_count_bar_graph(ax3,defect_log_table_data,flag)

                pdf_pages.savefig(fig)
                plt.close(fig)
# <-------------page two ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------>

                self.create_roll_details_table(current_date,defect_log_df, daily_rotation_counts,logo_img,pdf_pages)
                # ax5.text(text_x, text_y, f"Date: {current_date}", fontsize=28, color='black')
# <-------------page three ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------>

                rows_per_page = 40
                num_pages = -(-len(defect_log_table_data) // rows_per_page)
                for page_num in range(num_pages):
                    fig = self.create_defect_log_report(page_num,rows_per_page,defect_log_table_data,logo_img)
                    pdf_pages.savefig(fig)
                    plt.close(fig)
                
# <-------------page four ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------>
                
                fig = self.create_rpm_dotted_graph(current_date,logo_img)
                pdf_pages.savefig(fig)
                # Close the current figure to move to the next plot
                plt.close(fig)
                # Close the PDF file
                pdf_pages.close()




                # Reset the buffer position and return the PDF buffer
                pdf_buffer.seek(0)
                return pdf_buffer, True
        except Exception as e:
            print(str(e))
            return False

    def create_directory(self,report_date):
        filePath = config.get("path", "performance")
        millName = config.get("report", "millname")
        machinName = day_report_db.get_machine_name()
        PdfName = f"{millName}_{machinName}_Performance_{report_date}.pdf"
        directory = f"{filePath}/{PdfName}"
        os.makedirs(filePath, exist_ok=True)

        for filename in os.listdir(filePath):
            if filename.endswith(".pdf"):
                file_path = os.path.join(filePath, filename)
                os.remove(file_path)
        return directory

    def generate_performance_pdf(self,report_date):
        try:
            directory = self.create_directory(report_date)

            pdf_buffer, has_data = self.generate_pdf_plots(report_date, report_date)

            if has_data:
                with open(directory, "wb") as f:
                    f.write(pdf_buffer.getvalue())
                print(f"Performance report generated for {report_date}")
            else:
                print(f"No data found for {report_date}. PDF not generated.")
        except Exception as e:
            print(str(e))
            return False

    def generate_performace_report(self,user_input):
        try:
            self.generate_performance_pdf(user_input)
        except ValueError as e:
            print("Invalid date format. Please use YYYY-MM-DD format.")



