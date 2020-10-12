import PySimpleGUI as sg
import os.path
from client_pane import ClientPane
import client_layout
import subprocess

numClients = 10
clients = {}
clientIndex = 0

def create_client(name, clientIndex, channels, autoconnect):
    newClient = ClientPane(name, clientIndex, channels, autoconnect)


    clients[name] = newClient
    clientIndex += 1

    print(clients.keys())
    clientNames = []
    for k in clients.keys():
        clientNames.append(k)

    window["-CLIENT LIST-"].update(clientNames)

def event_loop():
    # Run the Event Loop
    while True:
        event, values = window.read()

        hasClients = False

        if len(clients) > 0:
            activeClient = clients[values["-CLIENT LIST-"][0]]
            hasClients = True

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-CREATE_CLIENT-":

            name = values["-CLIENT_NAME_INPUT-"]
            channels = values["-NUM_CHANNELS-"]

            # if name is already in use, popup an error
            if name in clients.keys():
                sg.popup('ERROR', 'Name already in use')
            else:
                create_client(name, clientIndex, channels, values['-AUTO_C-'])

        if event == "-CLIENT LIST-":  # Client is chosen from the listbox
            # window["-CLIENT_FRAME-"].expand(expand_x=True,expand_y=True,expand_row=True)
            window["-CLIENT_FRAME-"].update(activeClient.name)
            window["-ACTIVE_NAME-"].update(activeClient.name)
            window['-C_NUM_CHAN-'].update(activeClient.channels)
            window['-C_PORT_OFS-'].update(activeClient.port_offset)

        if event == '-CHANGE_ACTIVE-':
            activeClient.kill_server_thread()

        if event == '-DELETE_CLIENT-':
            activeClient.kill_server_thread()
            #figure out a way to remove from list on gui
            window["-CLIENT LIST-"].delete(activeClient.name)
            del clients[activeClient.name]


        if hasClients:
            # output stderr and stdout to console
            [out, err] = activeClient.read_server_thread()
            window['-LINE-OUTPUT-'].update(err)


    window.close()

if __name__ == '__main__':
    default_client = [[sg.Text("create a client")]]
    client_list_column = [
        [
            sg.Text("Client Name"),
            sg.In(size=(25, 1), enable_events=True, key="-CLIENT_NAME_INPUT-"),
            sg.Combo([1,2,3,4], default_value=1, key='-NUM_CHANNELS-'),
            sg.Button('CREATE CLIENT', key='-CREATE_CLIENT-'),
        ],
        [sg.Listbox(values=[], enable_events=True, bind_return_key=True, size=(40, 20), key="-CLIENT LIST-")],
        [sg.Button('Connect all', key='-C_ALL'), sg.Button('Disconnect all', key='D_ALL'), sg.Checkbox('Autoconnect', default=True, key='-AUTO_C-')],
    ]
    # ----- Full layout -----
    layout = [
        [
            sg.Column(client_list_column),
            sg.VSeperator(),
            sg.Column(client_layout.client_viewer_frame),
        ]
    ]
    window = sg.Window("JackTrip Client Manager", layout)

    event_loop()
