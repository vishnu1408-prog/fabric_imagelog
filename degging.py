from src.db import Reportdb
from day_report.image import ImageLog
from day_report.performance import Performance
from day_report.negative_uptime import NegetiveUptime
from src.report import Pdfgeneration,ShiftBasedReport

performance = Performance()
fabric_db = Reportdb()
imgae_log = ImageLog()
dayreport = Pdfgeneration(fabric_db)
shiftreport = ShiftBasedReport(fabric_db)
helper = NegetiveUptime()
class Debuger:
    def trigger_performance(self,day):
        performance.generate_performace_report(day)
        
    def trigger_fabric(self,day):
        dayreport.generate_report(day)

    def trigger_fabric_shift(self,day):
        shift = input("Enter the shift you want a,b or c :")
        shiftreport.Shift(day,shift.lower())

    def trigger_uptime(self,day):
        helper.uptime(day)
        
    def trigger_alaram_log(self,day):
        imgae_log.image(day)




if __name__=="__main__":
    debug = Debuger()
    date = '2024-03-15'
    # debug.trigger_fabric(date)
    # debug.trigger_fabric_shift(date)
    # debug.trigger_performance(date)
    # debug.trigger_alaram_log(date)
    # debug.trigger_uptime(date)
    
from src.db import Reportdb
from day_report.image import ImageLog
from day_report.performance import Performance
from day_report.negative_uptime import NegetiveUptime
from day_report.negative_uptime import GreenCamUptime
from src.report import Pdfgeneration,ShiftBasedReport



fabric_db = Reportdb()
imgae_log = ImageLog()
green_cam = GreenCamUptime()
helper = NegetiveUptime()
performance = Performance()
dayreport = Pdfgeneration(fabric_db)
shiftreport = ShiftBasedReport(fabric_db)


class Debuger:

    def trigger_performance(self,day):
        performance.generate_performace_report(day)
        
    def trigger_fabric(self,day):
        dayreport.generate_report(day)

    def trigger_fabric_shift(self,day):
        shift = input("Enter the shift you want a,b or c :")
        shiftreport.Shift(day,shift.lower())

    def trigger_uptime(self,day):
        helper.uptime(day)
        
    def trigger_alaram_log(self,day):
        imgae_log.image(day)

    def trigger_green_cam_log(self,day):
        green_cam.generate_green_cam_uptime(day)

if __name__=="__main__":
    debug = Debuger()
    date = '2024-04-20'

    
    input_report = input("Enter the report you want to generate :")
    if input_report == "1":
        debug.trigger_fabric(date)
    elif input_report == "2":
        debug.trigger_fabric_shift(date)
    elif input_report == "3":
        debug.trigger_performance(date)
    elif input_report == "4":
        debug.trigger_alaram_log(date)
    elif input_report == "5":
        debug.trigger_uptime(date)
    elif input_report == "6":
        debug.trigger_green_cam_log(date)
    else:
        print("Invalid input")
    