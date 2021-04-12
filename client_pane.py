import subprocess
from threading import Thread
import time

class ClientPane():

    def __init__(self, name, portOffset, channels, autoConnectAudio, zeroUnderrun, autoManage):
        self.name = name
        self.portOffset = portOffset
        self.channels = channels
        self.autoConnectAudio = autoConnectAudio
        self.zeroUnderrun = zeroUnderrun
        self.autoManage = autoManage

        self.isActive = False
        self.connectionActive = False
        self.connectionChanged = False
        self.requestRestart = False
        self.currentOutput = ''

        self.connectionQuality = 1.0 # overall quality 0-1
        self.UDP_wait_count = 0
        self.skew = 0.0

        print(f'setting up client {name} on port {4464 + portOffset}')

        # autoManage immediately runs server thread upon creation
        if autoManage:
            self.run_server_thread()

    def server_command(self):
        if self.isActive:
            self.kill_server_thread()

        #time.sleep(0.1)

        jtCommand = ["jacktrip", "-s",
            "--clientname", self.name, 
            "-n", str(self.channels),
            "-o", str(self.portOffset), 
            "--iostat", str(1)]

        if self.zeroUnderrun:
            jtCommand.append("-z")

        if self.autoConnectAudio == False:
            jtCommand.append("--nojackportsconnect")

        print(f"Running JT Server: {jtCommand}")

        self.server_thread = subprocess.Popen(jtCommand, stdout=subprocess.PIPE)
        self.isActive = True
        self.server_runtime()


    def server_runtime(self):
        while True:
            output = self.server_thread.stdout.readline()

            if output == '' and self.server_thread.poll() is not None:
                break

            if output:
                self.currentOutput = str(output.strip(), 'utf-8')
                self.filter_events(self.currentOutput) # filter stdout
                
                if self.autoManage:
                    self.connection_behavior() # apply connection rules

                # if not self.connectionActive and 'Received Connection from Peer' in self.currentOutput:
                #     self.connectionActive = True
                #     self.interface.update_client_listboxbox()

        rc = self.server_thread.poll()

    def change_port(self, port):
        print(f"Changing {self.name} port to {port}")
        self.portOffset = port
        self.restart_server()

    def restart_server(self):
        print(f"Restarting {self.name} server")
        self.kill_server_thread()
        time.sleep(0.1)
        self.run_server_thread()

    def connection_behavior(self):
        self.connectionQuality = self.calculate_quality()
        # if self.UDP_wait_count > 10:
        #     window['-C_QUALITY-'].update('UNSTABLE', text_color='red')
        # else:
        #     window['-C_QUALITY-'].update('GOOD', text_color='black')
        # in event that quality drops below desired level, re-try connection
        if self.connectionQuality < 0.01:
            print(f'server terminating {self.name}, quality too low!')

            if self.autoManage:
                # self.requestRestart = True
                self.connectionActive = False
                self.connectionQuality = 1.0 # this could eventually roll over

            self.kill_server_thread()
            time.sleep(0.3)
            self.run_server_thread()

    # representation of connection quality (work in progress)
    # this can determine their level in the mix (to be implemented later)
    # if quality is 0.0, the connection will be terminated or retried, based on session settings
    def calculate_quality(self):
        if self.UDP_wait_count > 10:
            quality = 0.0
        elif self.skew > 0:
            # quality = self.connectionQuality
            quality = 1/((abs(self.skew) * 0.1) + 1 + 1e-7)
        else: # in this case the server may be lagging (negative skew)
            quality = 1.0
        return quality

    # filter stdout from jt process
    def filter_events(self, output):
        # in this case, will it say this if a client disconnects and reconnects?
        if not self.connectionActive and 'Received Connection from Peer' in output:
            self.connectionActive = True

        if self.connectionActive:
            # determine if client has bad connection
            if 'UDP waiting too long' in output:
                self.UDP_wait_count += 1
            elif self.UDP_wait_count > 0:
                self.UDP_wait_count -= 1

            if 'skew' in output:
                # remember to make sure if this goes over 4 digits to term thread
                skew = self.filter_string('skew: ', output, 4)
                self.skew = int(skew)


    def filter_string(self, string, input, length):
        # string = string to match in input, length concats
        str_len = len(string)
        idx = input.index(string)
        extracted_str = input[idx+str_len:idx+str_len+length]
        return extracted_str


    def run_server_thread(self):
        print('starting jacktrip server')
        t = Thread(target=self.server_command, daemon=True)
        t.start()

    def read_server_thread(self):
        return self.currentOutput

    def kill_server_thread(self):
        print(f'killing server thread for {self.name}')
        self.server_thread.kill()
        self.isActive = False
        self.connectionActive = False
        # os.remove(f'client_log_{self.name}')

    def get_connection_status(self):
        status = []
        return status

    # returns client info for saving session
    def get_client_info(self):
        return [self.name, 
                str(self.portOffset), 
                str(self.channels), 
                str(int(self.autoConnectAudio)), 
                str(int(self.zeroUnderrun)), 
                str(int(self.autoManage))]