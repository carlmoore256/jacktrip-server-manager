import PySimpleGUI as sg
import subprocess
from threading import Thread
import sys
import shlex
from joblib import Parallel, delayed

class ClientPane():

    def __init__(self, name, port_offset, channels, autoconnect):
        self.name = name
        self.port_offset = port_offset
        self.channels = channels
        self.autoconnect = autoconnect

        # autoconnect immediately runs server thread upon creation
        if autoconnect:
            self.run_server_thread()

    def server_command(self):

        self.server_thread = subprocess.Popen(["jacktrip", "-s",
        "--clientname", self.name,
         "-n", str(self.channels),
         "-o", str(self.port_offset)],
         stdout=subprocess.PIPE,)


        log_file = open(f'log_{self.name}', 'ab+')

        while True:
            output = self.server_thread.stdout.readline()

            if output == '' and self.server_thread.poll() is not None:
                break

            if output:
                print(output.strip())
                log_file.write(output.strip())

        rc = self.server_thread.poll()
        log_file.close()
        print(rc)

    def run_server_thread(self):
        # run the jacktrip command here
        print('starting jacktrip server')
        print(f"jacktrip -s --clientname {self.name} -n {self.channels} -o {self.port_offset}")

        x = Thread(target=self.server_command, daemon=True)
        x.start()
        # self.server_thread = subprocess.Popen(["jacktrip", "-s",
        # "--clientname", self.name,
        #  "-n", str(self.channels),
        #  "-o", str(self.port_offset)],
        #  stdout=subprocess.PIPE,)

        # while True:
        #     output = self.server_thread.stdout.readline()
        #     if output == '' and self.server_thread.poll() is not None:
        #         break
        #     if output:
        #         print(output.strip())
        #     rc = self.server_thread.poll()
        #
        # print(rc)



    def read_server_thread(self):

        # while True:
        #     out = self.server_thread.stderr.read(1)
        #     if out == '' and self.server_thread.poll() != None:
        #         break
        #     if out != '':
        #         sys.stdout.write(str(out))
        #         sys.stdout.flush()

        err = ''
        out = ''
        return out, err


    def kill_server_thread(self):
        self.server_thread.kill()

    def get_connection_status(self):
        status = []
        return status
