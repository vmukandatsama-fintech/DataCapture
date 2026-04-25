import sys
import os

# Must be at module level so Django can find config/ when the service starts
APP_DIR = r'C:\DataCapture'
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import win32serviceutil
import win32service
import win32event
import servicemanager


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
        # Tell Windows the service is running before blocking on Waitress
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ''),
        )
        try:
            from waitress import serve
            from config.wsgi import application
            serve(application, host='0.0.0.0', port=8000, threads=8)
        except Exception as e:
            log_dir = os.path.join(APP_DIR, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, 'service_error.log'), 'a') as f:
                import traceback, datetime
                f.write(f"\n{datetime.datetime.now()} STARTUP ERROR\n")
                f.write(traceback.format_exc())
            raise


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DataCaptureService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DataCaptureService)
