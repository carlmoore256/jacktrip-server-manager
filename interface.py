import PySimpleGUI as sg
import os.path
from client_pane import ClientPane
import client_layout
import subprocess


class Interface():

    def __init__(self):
        self.terminate_jacktrip() # clean up existing processes
        self.clients = {}

        default_client = [[sg.Text("create a client")]]
        client_list_column = [
            [
                sg.Text("Client Name"),
                sg.In(size=(25, 1), enable_events=True, key="-CLIENT_NAME_INPUT-"),
                sg.Combo([1,2,3,4], default_value=1, key='-NUM_CHANNELS-'),
                sg.Button('CREATE', key='-CREATE_CLIENT-'),
            ],
            [sg.Listbox(values=[], enable_events=True, bind_return_key=True, size=(34, 15), font='ANY 14', key="-CLIENT LIST-")],
            [sg.Button('Connect all', key='-C_ALL-'), sg.Button('Disconnect all', key='-D_ALL-'), sg.Checkbox('Autoconnect', default=True, key='-AUTO_C-')],
        ]
        # ----- Full layout -----
        layout = [
            [
                sg.Column(client_list_column),
                sg.VSeperator(),
                sg.Column(client_layout.client_viewer_frame),
            ]
        ]
        self.window = sg.Window("JackTrip Client Manager", layout)
        # initial draw
        # event, values = self.window.read()

        self.event_loop()

    def update_client_listbox(self):
        clientNames = []
        for k in self.clients.keys():
            thisKey = k
            # polls connection status and marks accordingly
            if self.clients[k].connectionActive:
                thisKey = f'✓ {thisKey}'
            else:
                thisKey = f'  {thisKey}'
            clientNames.append(thisKey)

        self.window["-CLIENT LIST-"].update(clientNames)

    def create_client(self, name, clientIndex, channels, autoconnect):
        newClient = ClientPane(self, name, clientIndex, channels, autoconnect)
        self.clients[name] = newClient
        self.update_client_listbox() # updates list of self.clients

    def terminate_jacktrip(self):
        print('terminating existing jacktrip processes')
        subprocess.run(['killall', 'jacktrip'])

    def event_loop(self):
        # Run the Event Loop

        while True:
            event, values = self.window.read(timeout=300)
            # event, values = self.window.read()

            hasClients = False

            if len(self.clients) > 0:
                try:
                    activeClient = self.clients[values["-CLIENT LIST-"][0][2:]]
                    hasClients = True
                except:
                    print('no client selection yet')

            if event == "Exit" or event == sg.WIN_CLOSED:
                # terminate_jacktrip()
                for c in self.clients.keys():
                    self.clients[c].kill_server_thread()
                break

            if event == "-CREATE_CLIENT-":

                name = values["-CLIENT_NAME_INPUT-"]
                channels = values["-NUM_CHANNELS-"]

                # if name is already in use, popup an error
                if name in self.clients.keys():
                    sg.popup('ERROR', 'Name already in use')
                else:
                    self.create_client(name, len(self.clients), channels, values['-AUTO_C-'])

            if hasClients:

                if event == '-DELETE_CLIENT-':
                    activeClient.kill_server_thread()
                    del self.clients[activeClient.name]
                    self.update_client_listbox()

                if event == '-C_ALL-':
                    for c in self.clients.keys():
                        self.clients[c].run_server_thread()

                if event == '-D_ALL':
                    for c in self.clients.keys():
                        self.clients[c].kill_server_thread()

                activeClient.gui_update(event, self.window)
            else:
                client_layout.reset_view(self.window)
                # event, values = self.window.read()


        self.window.close()


if __name__ == '__main__':
    mainInterface = Interface()
