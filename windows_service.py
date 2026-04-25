import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager

APP_DIR = r'C:\DataCapture'


class DataCaptureService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'DataCapture'
    _svc_display_name_ = 'DataCapture Web App'
    _svc_description_ = 'CY26 Data Capture — Waitress on port 8000'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ''),
        )
        self.main()

    def main(self):
        os.chdir(APP_DIR)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        from waitress import serve
        from config.wsgi import application
        serve(application, host='0.0.0.0', port=8000, threads=8)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DataCaptureService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DataCaptureService)
