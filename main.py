import json
from src.db import Reportdb
from fastapi import FastAPI
from src.config import Config
from pydantic import BaseModel
from day_report.image import ImageLog
from day_report.performance import Performance
from src.report import Pdfgeneration,ShiftBasedReport
from day_report.negative_uptime import NegetiveUptime
from day_report.negative_uptime import GreenCamUptime

app = FastAPI()


config = Config()


# sample json format
class Report(BaseModel):
    name: str
    data: str


@app.get("/")
def index():
    return {"message": "Forbidden"}

@app.post("/fabric_report/")
async def generating_fabric_report(item: Report):
    data = json.loads(item.data)
    # {"report_type":"day","date":"2023-12-14"}
    # {"report_type":"a","date":"2023-12-14"}
    # {"report_type":"b","date":"2023-12-14"}
    # {"report_type":"c","date":"2023-12-14"}

    # day
    if data["report_type"] == "day":
        try:
            db = Reportdb()
            pdf = Pdfgeneration(db=db)
            pdf.generate_report(data["date"])
            data["status"] = True
            return data
        except Exception:
            data["status"] = False
            return data
    # shift
    elif (
        data["report_type"] == "a"
        or data["report_type"] == "b"
        or data["report_type"] == "c"
    ):
        try:
            db = Reportdb()
            pdf = ShiftBasedReport(db=db)
            pdf.Shift(date=data["date"], shift=data["report_type"])
            data["status"] = True
            return data
        except Exception:
            data["status"] = False
            return data

@app.post("/performance/")
async def generating_performance_report(item: Report):
    try:
        data = json.loads(item.data)
        performance = Performance()
        performance.generate_performace_report(data["date"])
        data["status"] = True
        return data
    except Exception:
        data["status"] = False
        return data

@app.post("/uptime/")
async def generating_uptime_report(item: Report):
    try:
        data = json.loads(item.data)
        uptime = NegetiveUptime()
        uptime.uptime(data["date"])
        data["status"] = True
        return data
    except Exception:
        data["status"] = False
        return data

@app.post("/greencam_uptime/")
async def generating_uptime_report(item: Report):
    try:
        data = json.loads(item.data)
        uptime = GreenCamUptime()
        uptime.generate_green_cam_uptime(data["date"])
        data["status"] = True
        return data
    except Exception:
        data["status"] = False
        return item


@app.post("/image/")
async def generating_image_report(item: Report):
    try:
        data = json.loads(item.data)
        img = ImageLog()
        img.image(data["date"])
        data["status"] = True
        return data
    except Exception:
        data["status"] = False
        return data

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="localhost", port=8003)