# -*- coding: utf-8 -*-

### built-in ###
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import os
import subprocess
from datetime import datetime

# path to manage.py file
MANAGE_FILE = r'D:\Documentos\Programming\Python\spec\net_sync\src\manage.py'
# path to netsync log file
LOG_FILE = r'C:\ProgramData\NetSync\netsync.log'
# minutes to refresh
TIMING = 1

# system constants
LOG_PATH = os.path.dirname(LOG_FILE)

class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = 'netSync'
    _svc_display_name_ = 'NetSync Cron Service'
    _svc_description_ = 'Cron service for NetSync'

    def __init__(self, args):
        super().__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def ensure_log_folder(self):
        # create folder if not exist
        # raise if error
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

    def SvcStop(self):
        self.stop()

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.start()

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def start(self):
        # ensure log folder
        self.ensure_log_folder()

        # start process
        with open(LOG_FILE, mode='a+', encoding='utf-8') as logg:
            logg.write('{} Starting service...\n'.format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ))

        self.isrunning = True

    def stop(self):
        # ensure log folder
        self.ensure_log_folder()

        # stop process
        with open(LOG_FILE, mode='a+', encoding='utf-8') as logg:
            logg.write('{} Stoping service...\n'.format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ))

        self.isrunning = False

    def main(self):
        # main process
        while self.isrunning:
            # ensure log folder
            self.ensure_log_folder()

            # main process
            with open(LOG_FILE, mode='a+', encoding='utf-8') as logg:
                try:
                    p = subprocess.check_call(
                        ['python', MANAGE_FILE, 'run_syncs'],
                        stdout=logg,
                        shell=True
                    )
                except Exception as error:
                    logg.write('{} Command Error: {}.\n'.format(
                        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        str(error)
                    ))
            time.sleep(TIMING * 60)


if __name__ == '__main__':
    # create service with custom class
    win32serviceutil.HandleCommandLine(AppServerSvc)
