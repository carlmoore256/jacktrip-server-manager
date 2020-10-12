import PySimpleGUI as sg
import subprocess
from threading import Thread
import sys
import shlex
from joblib import Parallel, delayed
import time
import os

class ClientPane():

    def __init__(self, interface, name, port_offset, channels, autoconnect):
        self.interface = interface
        self.name = name
        self.port_offset = port_offset
        self.channels = channels
        self.autoconnect = autoconnect
        self.isActive = False
        self.connectionActive = False
        self.connectionChanged = False
        self.currentOutput = ''

        print(f'setting up client {name} on port {4464 + port_offset}')
        # autoconnect immediately runs server thread upon creation
        if autoconnect:
            self.run_server_thread()

    def server_command(self):
        # make sure the server isnt already running
        if self.isActive:
            self.kill_server_thread()

        time.sleep(0.1)
        self.server_thread = subprocess.Popen(["jacktrip", "-s",
        "--clientname", self.name, "-n", str(self.channels),
        "-o", str(self.port_offset), "--iostat", str(1)],
        stdout=subprocess.PIPE,)

        self.isActive = True

        # log_file = open(f'client_log_{self.name}', 'ab+')

        while True:
            output = self.server_thread.stdout.readline()

            if output == '' and self.server_thread.poll() is not None:
                break

            if output:
                self.currentOutput = str(output.strip(), 'utf-8')
                print(self.currentOutput)

                if not self.connectionActive and 'Received Connection from Peer' in self.currentOutput:
                    self.connectionActive = True
                    self.interface.update_client_listbox()

        rc = self.server_thread.poll()


    def gui_update(self, event, window):
        window['-LINE-OUTPUT-'].update(self.currentOutput)
        window['-ML1-'+sg.WRITE_ONLY_KEY].print(f'{self.currentOutput}\n', end='')

        if self.connectionActive:
            window['-CONNECT_STATUS-'].update('CONNECTED!', text_color='yellow')
        else:
            window['-CONNECT_STATUS-'].update('NOT CONNECTED', text_color='black')

        if event == '-CHANGE_ACTIVE-':
            if self.isActive:
                self.kill_server_thread()
                window['-CHANGE_ACTIVE-'].update('Enable')
                window['-CHANGE_ACTIVE-'].Update(button_color=('black', 'green'))
            else:
                self.run_server_thread()
                window['-CHANGE_ACTIVE-'].update('Disable')
                window['-CHANGE_ACTIVE-'].Update(button_color=('black', 'red'))

    def run_server_thread(self):
        print('starting jacktrip server')
        print(f"jacktrip -s --clientname {self.name} -n {self.channels} -o {self.port_offset}")

        x = Thread(target=self.server_command, daemon=True)
        x.start()


    def read_server_thread(self):
        return self.currentOutput


    def kill_server_thread(self):
        print(f'killing server thread {self.server_thread}')
        self.server_thread.kill()
        self.isActive = False
        self.connectionActive = False
        # os.remove(f'client_log_{self.name}')

    def get_connection_status(self):
        status = []
        return status
