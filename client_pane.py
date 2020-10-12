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

        self.connectionQuality = 1.0 # overall quality 0-1
        self.skew = 0.0
        self.UDP_wait_count = 0
        # clientPane can request a server restart on next update loop
        # if autoconnect is enabled
        self.requestRestart = False

        print(f'setting up client {name} on port {4464 + port_offset}')
        # autoconnect immediately runs server thread upon creation
        if autoconnect:
            self.run_server_thread()
            self.interface.window['-CHANGE_ACTIVE-'].update(button_color=('black', 'green'))
        else:
            self.interface.window['-CHANGE_ACTIVE-'].update(button_color=('black', 'red'))

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

        while True:
            output = self.server_thread.stdout.readline()

            if output == '' and self.server_thread.poll() is not None:
                break

            if output:
                self.currentOutput = str(output.strip(), 'utf-8')
                # print(self.currentOutput)
                # filter stdout events
                self.filter_events(self.currentOutput)
                # apply connection rules
                self.connection_behavior()

                # if not self.connectionActive and 'Received Connection from Peer' in self.currentOutput:
                #     self.connectionActive = True
                #     self.interface.update_client_listbox()

        rc = self.server_thread.poll()

    def connection_behavior(self):
        self.connectionQuality = self.calculate_quality()
        # if self.UDP_wait_count > 10:
        #     window['-C_QUALITY-'].update('UNSTABLE', text_color='red')
        # else:
        #     window['-C_QUALITY-'].update('GOOD', text_color='black')
        # in event that quality drops below desired level, re-try connection
        if self.connectionQuality < 0.01:
            print(f'server terminating {self.name}, quality too low!')

            if self.autoconnect:
                self.requestRestart = True
                self.connectionActive = False
                self.connectionQuality = 1.0 # this could eventually roll over

            self.kill_server_thread()


    def calculate_quality(self):
        # make calculation of connection Quality
        # this can determine their level in the mix
        # if quality is 0.0, the connection will be terminated
        # and possibly retried
        if self.UDP_wait_count > 10:
            quality = 0.0
        elif self.skew > 0:
            # quality = self.connectionQuality

            quality = 1/((abs(self.skew) * 0.1) + 1 + 1e-7)
        else: # in this case the server may be lagging (negative skew)
            quality = 1.0

        print(f'QUALITY {quality}')
        return quality

    def filter_events(self, output):
        if not self.connectionActive and 'Received Connection from Peer' in output:
            self.connectionActive = True
            self.interface.update_client_listbox()

        if self.connectionActive:
            # determine if client has bad connection
            if 'UDP waiting too long' in output:
                self.UDP_wait_count += 1
            elif self.UDP_wait_count > 0:
                self.UDP_wait_count -= 1

            if 'skew' in output:
                # remember to make sure if this goes over 4 digits to term thread
                skew = self.filter_string('skew: ', output, 4)
                print(f'{skew} SKEW')
                self.skew = int(skew)


    def filter_string(self, string, input, length):
        # string = string to match in input, length concats
        str_len = len(string)
        idx = input.index(string)
        extracted_str = input[idx+str_len:idx+str_len+length]
        return extracted_str

    def gui_update(self, event, window):
        # in the event clientPane asks for a restart
        if self.requestRestart:
            print(f'client {self.name} restarting server thread')
            self.run_server_thread()

        # update text output
        window['-LINE-OUTPUT-'].update(self.currentOutput)
        window['-ML1-'+sg.WRITE_ONLY_KEY].print(f'{self.currentOutput}\n', end='')

        # update client statistics
        window["-CLIENT_FRAME-"].update(self.name)
        window['-C_NUM_CHAN-'].update(self.channels)
        window['-C_PORT_OFS-'].update(self.port_offset)

        if self.connectionActive:
            print('connection active!!!')
            window['-CONNECT_STATUS-'].update('CONNECTED!', text_color='yellow')
            # quality = self.calculate_quality()
            window['-C_QUALITY_RATING-'].update('{:10.2f}'.format(self.connectionQuality))
            window['-C_SKEW-'].update(str(self.skew))

        else:
            window['-CONNECT_STATUS-'].update('NOT CONNECTED', text_color='white')
            window['-C_QUALITY-'].update('-')
            window['-C_SKEW-'].update('-')

        if event == '-CHANGE_ACTIVE-':
            if self.isActive:
                self.kill_server_thread()
                window['-CHANGE_ACTIVE-'].update('Enable')
                window['-CHANGE_ACTIVE-'].Update(button_color=('black', 'green'))
            else:
                self.run_server_thread()
                window['-CHANGE_ACTIVE-'].update('Disable')
                window['-CHANGE_ACTIVE-'].Update(button_color=('black', 'red'))

        if self.connectionQuality > 0.5:
            window['-C_QUALITY-'].update('GOOD', text_color='yellow')

        if self.connectionQuality <= 0.5:
            window['-C_QUALITY-'].update('UNSTABLE', text_color='red')


    def run_server_thread(self):
        self.requestRestart = False
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
