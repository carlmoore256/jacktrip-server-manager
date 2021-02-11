# from main import JTSession
from client_pane import ClientPane
from interface import Interface

import csv
import subprocess

# handles the jacktrip session threads and program operations
class Session():

    def __init__(self):
        self.terminate_jacktrip() # terminate existing threads
        self.clients = []

    # save a session to csv format
    def save_session(self, filepath):
        if filepath is None:
            return
        filepath = filepath + ".csv"
        with open(filepath, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for c in self.clients:
                csvwriter.writerow(c.get_client_info())
        print(f"session file saved to {filepath}")
    
    # loads a session from a config file (csv)
    # <clientName>,<portOffset>,<numChannels>,<autoConnectAudioToHardware>,<zerounderrun>,<autoManageConnection>
    def load_session(self, filepath, terminate_existing=True):
        if terminate_existing:
            for c in self.clients:
                self.delete_client(c)

        with open(filepath, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            # fields = next(csvreader) # get the column fields
            for row in csvreader:
                self.create_client(
                    name=row[0], 
                    portOffset=int(row[1]),
                    channels=int(row[2]),
                    autoConnectAudio=bool(int(row[3])),
                    zeroUnderrun=bool(int(row[4])),
                    autoManage=bool(int(row[5])))

    # return all existing names
    def existing_names(self):
        names = []
        for c in self.clients:
            names.append(c.name)
        return names

    # return client by name
    def client_by_name(self, name):
        for c in self.clients:
            if c.name == name:
                return c
        return None

    # return a set of labels with an indication of their connection status
    def client_label_status(self):
        client_labels = []
        for c in self.clients:
            if c.isActive:
                if c.connectionActive:
                    client_labels.append(f"✓ {c.name}")
                else:
                    client_labels.append(f"o {c.name}")
            else:
                client_labels.append(f"  {c.name}")
        return client_labels

    # get the lowest number port offset not already in use
    def find_empty_port(self):
        used_ports = [c.portOffset for c in self.clients]
        port = 0
        while port in used_ports:
            port += 1
        return port

    # find a new name if it already exists
    def alternate_name(self, name):
        newName = name
        allNames = self.existing_names()
        i = 1
        while newName in allNames:
            newName = f'{name} ({i})'
            i += 1
        return newName

    # create a new client in the session, portOffset auto assigned if None
    def create_client(self, name, portOffset, channels, autoConnectAudio, zeroUnderrun, autoManage):
        # check if name is already in use
        if name in self.existing_names():
            name = self.alternate_name(name)

        # if not specified, offset will be next available port
        if portOffset is None:
            portOffset = self.find_empty_port()

        # create the new client
        newClient = ClientPane(name, portOffset, channels, autoConnectAudio, zeroUnderrun, autoManage)
        self.clients.append(newClient)

    def activate_all(self):
        for c in self.clients:
            c.run_server_thread()

    # deactivate all connections but keep clients
    def deactivate_all(self):
        for c in self.clients:
            c.kill_server_thread()

    def delete_all(self):
        for c in self.clients:
            self.delete_client(c)

    def delete_client(self, client):
        client.kill_server_thread()
        self.clients.remove(client)

    # terminates any existing running jacktrip processes
    def terminate_jacktrip(self):
        print('terminating existing jacktrip processes')
        subprocess.run(['killall', 'jacktrip'])

# DELETE ME ==============================================
    # check whether there are any existing clients
    # def check_if_clients(self):
    #     if len(self.clients) > 1:
    #         return True
    #     else:
    #         return False