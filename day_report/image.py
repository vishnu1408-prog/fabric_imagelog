import psycopg2, os
import pandas as pd
from io import BytesIO
from src.config import Config
from reportlab.lib import colors
from PIL import Image as PilImage
from day_report.db import DayReportDb
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer


config = Config()
day_report_db = DayReportDb()

global roll_name_status
global Score_status
global bypass_status

class ImageLog:
    def image(self,user_date):
        # Establish a connection to the PostgreSQL database
        try:
            conn = psycopg2.connect(
                host="localhost", database="knitting", user="postgres", password="55555"
            )

            # Define your SQL query with the user-provided date
            query = f"""
            SELECT dd.defect_id, dd.add_imagepath as file_path, dd.filename, TO_CHAR(dd.timestamp, 'YYYY-MM-DD HH24:MI:SS') AS formatted_timestamp, dd.coordinate, dt.defect_name,dd.bypass_state,dd.roll_id,dd.score
            FROM defect_details AS dd
            INNER JOIN alarm_status AS a ON dd.defect_id = a.defect_id
            INNER JOIN defect_type AS dt ON dd.defecttyp_id = dt.defecttyp_id
            WHERE DATE(dd.timestamp) = '{user_date}';
            """
            roll_name_status = eval(config.get("trigger", "roll_name"))
            bypass_status = eval(config.get("trigger", "bypass_status"))
            Score_status = eval(config.get("trigger", "Score"))
            # Use pandas to read the data directly into a DataFrame
            df = pd.read_sql_query(query, conn)
            if len(df) == 0:
                df["defect_id"] = ["1112129"]
                df["file_path"] = ["data/186/2023-12-27/voltcam/defect/unbox/twoply/"]
                df["filename"] = ["mkl"]
                df["formatted_timestamp"] = ["0000-00-00 00:00:00"]
                df["coordinate"] = ["[575.397705078125, 3.671722412109375]"]
                df["defect_name"] = ["Nill"]
                roll_name_status = bypass_status = Score_status = False

            df.sort_values(by=["formatted_timestamp"], ascending=[True], inplace=True)
            
            roll_name = []
            for index, row in df.iterrows():
                if not pd.isnull(row["roll_id"]):
                    roll_name.append(day_report_db.get_roll_name(str(row["roll_id"])))

            columns_to_drop = ["defect_id", "coordinate", "roll_id"]
            filtered_df = df.drop(columns_to_drop, axis=1)
            if roll_name!=[]:
                filtered_df["roll_name"] = roll_name

            # Split the formatted_timestamp column into separate date and time columns
            date_time_split = filtered_df["formatted_timestamp"].str.split(" ", expand=True)

            filtered_df["Date"] = date_time_split[0]
            filtered_df["Time"] = date_time_split[1]
            filtered_df.drop("formatted_timestamp", axis=1, inplace=True)
            filtered_df["bypass_state"].replace("2", "OFF", inplace=True)
            filtered_df["bypass_state"].replace("1", "ON", inplace=True)

            # Sort the DataFrame by 'Date', 'Time', and 'Defect_name' columns
            filtered_df.sort_values(
                by=["Date", "Time", "defect_name"],
                ascending=[True, True, True],
                inplace=True,
            )

            filtered_df.sort_values(
                by=["Date", "Time", "defect_name"],
                ascending=[True, True, True],
                inplace=True,
            )

            lables = ["Date", "Time", "defect_name", "filename", "file_path"]
            table_label = []
            if roll_name_status:
                lables = lables + ["roll_name"]
                table_label.append("roll_name")
            if bypass_status:
                lables = lables + ["bypass_state"]
                table_label.append("bypass_state")
            if Score_status:
                lables = lables + ["score"]
                table_label.append("score")

            filtered_df = filtered_df[lables]

            # Create a PDF document
            pdf_buffer = BytesIO()
            pdf_title = f"Alarm Log for {user_date}"  # Set the PDF title dynamically
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, title=pdf_title)
            elements = []

            static_path = "./knitting-core"
            for _, row in filtered_df.iterrows():
                # Create a table for the new page with the desired columns (excluding file_path and filename)
                lables = ["Date", "Time", "defect_name"] + table_label
                table_data = [row[lables].tolist()]  # Table row
                table = Table(table_data)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )
                elements.append(table)
                elements.append(Spacer(1, 12))  # Add space after the table

                file_path = row["file_path"].strip("/")  # Remove leading/trailing slashes
                filename = row["filename"]  # Get the filename from the current row
                full_file_path = os.path.normpath(os.path.join(static_path, file_path))
                for root, dirs, files in os.walk(full_file_path):
                    for file in files:
                        if file == filename:
                            image_path = os.path.join(
                                root, file
                            )  # Construct the full image path

                            try:
                                pil_image = PilImage.open(image_path)
                                pil_image.thumbnail(
                                    (200, 200)
                                )  # Resize the image as needed
                                img = Image(image_path, 450, 255)  # Use the full image path
                                elements.append(img)
                                elements.append(Spacer(1, 12))  # Add space after the image
                            except Exception as e:
                                print(f"Error loading image at {image_path}: {e}")
            # Build the PDF document
            doc.build(elements)

            # Save the PDF to a file
            machinName = day_report_db.get_machine_name()
            filePath = config.get("path", "image")
            millName = config.get("report", "millname")
            PdfName = f"{millName}_{machinName}_Image_Log_{user_date}.pdf"
            directory = f"{filePath}/{PdfName}"

            os.makedirs(filePath, exist_ok=True)

            for filename in os.listdir(filePath):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(filePath, filename)
                    os.remove(file_path)

            with open(directory, "wb") as f:
                f.write(pdf_buffer.getvalue())
                print(f"PDF saved as {PdfName}")

        except (Exception, psycopg2.Error) as e:
            import traceback

            traceback.print_exc()
            print("Error connecting to the database:", e)