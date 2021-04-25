import client_layout
import signal_router

import PySimpleGUI as sg
import os.path
import subprocess

# handles all GUI interaction and updates
class Interface():

    def __init__(self, session):
        self.selectedClient = 0
        
        self.Session = session
        self.window = sg.Window("JackTrip Session Manager", self.generate_layout())
        self.event_loop() # begin main program loop

    # generate the initial full layout
    def generate_layout(self):
        default_client = [[sg.Text("create a client")]]
        client_list_column = [
            [   
                sg.Text("Client Name"),
                sg.In(size=(25, 1), enable_events=True, key="_name"),
                sg.Combo([1,2,3,4], default_value=1, key='_create_num_ch'),
                sg.Button('CREATE', key='_create'), ],
                
            [sg.Listbox(values=[], enable_events=True, bind_return_key=True, size=(34, 30), 
                        font='ANY 14', key="_client_listbox")],
            
            [   
                sg.Button('Activate all', key='_activate_all'), 
                sg.Button('Deactivate all', key='_deactivate_all'), 
                sg.Button('Save Session', key='_save_sess'),
                sg.Button('Load Session', key='_load_sess'),
                # sg.Button('Route All Clients', key='_route_all'),
            ],
            [
                sg.Checkbox('AutoManage', default=True, key='_automanage'),

            ],
        ]
        layout = [ # Full interface layout
            [
                sg.Column(client_list_column),
                sg.VSeperator(),
                sg.Column(client_layout.client_viewer_frame),
            ]
        ]
        return layout

    # clear stats when no clients exist
    def display_empty_client(self):
        self.window['_connect_status'].update('-') 
        self.window['_quality'].update('-')
        self.window['_quality_label'].update('-')
        self.window['_num_ch'].update('-')
        self.window['_change_active'].update(button_color=('gray', 'white'))

    # updates all client labels in the listbox (left side)
    # returns activeClient, currently selected client
    # selectionChanged, bool indicating if client has changed from last frame
    def update_client_listboxbox(self, values):
        if len(values['_client_listbox']) > 0:
            clientName = values["_client_listbox"][0][2:]
            activeClient = self.Session.client_by_name(clientName)
        else:
            activeClient = None
        
        selIndex = self.window['_client_listbox'].get_indexes()
        prevSelectedClient = self.selectedClient

        if len(selIndex) > 0:
            self.selectedClient = selIndex[0]

        status_labels = self.Session.client_label_status()
        self.window["_client_listbox"].update(status_labels, set_to_index=self.selectedClient)

        selectionChanged = False
        if prevSelectedClient != self.selectedClient:
            selectionChanged = True

        return activeClient, selectionChanged


    # updates client information display (right side)
    def update_client_pane(self, client, event, selectionChanged):
        self.window["_client_frame"].update(client.name)

        self.window['_console_line'].update(client.currentOutput)

        if selectionChanged:
            self.window['_console_scroll' + sg.WRITE_ONLY_KEY].update(value='')

        self.window['_console_scroll' + sg.WRITE_ONLY_KEY].print(f'{client.currentOutput}\n', end='')

        self.window['_num_ch'].update(client.channels)
        self.window['_offset'].update(client.portOffset)
        self.window['_automan_client'].update(client.autoManage)

        
        self.window['_client_routing'].update(client.connectedPeers)

        if client.connectionActive:
            self.window['_connect_status'].update('Connected', text_color='white')
            self.window['_quality_label'].update('{:10.2f}'.format(client.connectionQuality))
            self.window['_skew'].update(str(client.skew))
            if client.connectionQuality > 0.5:
                self.window['_quality'].update('Good', text_color='white')
            else:
                self.window['_quality'].update('Unstable', text_color='red')
        else:
            self.window['_connect_status'].update('Not Connected', text_color='red')
            self.window['_quality'].update('-')
            self.window['_skew'].update('-')

        if event == '_change_active':
            if client.isActive:
                client.kill_server_thread()
                self.window['_change_active'].update('Activate')
                self.window['_change_active'].Update(button_color=('black', 'green'))
            else:
                client.run_server_thread()
                self.window['_change_active'].update('Deactivate')
                self.window['_change_active'].Update(button_color=('black', 'red'))




    # def update_client_routing(self):


    def file_browser(self):
        filepath = sg.popup_get_file('Select session file')
        return filepath

    def folder_browser(self):
        filepath = sg.popup_get_folder('Select save directory')
        return filepath

    def text_entry(self, win_title):
        text = sg.popup_get_text(win_title)
        return text

    def error_popup(self, title, header):
        sg.popup_error(title, header)

    def ok_cancel_popup(self, message):
        result = sg.Popup(message, button_type=4)
        return result

    def port_change(self, port, client):

        for digit in port:
            if not digit.isdigit():
                self.error_popup("Error", "Port entry contains strings, only digits allowed")
                return
        else:
            port = int(port)

        if port in self.Session.used_ports():
            client_using = self.Session.client_by_port(port)
            if client_using == None:
                client.change_port(port)
                return
            result = self.ok_cancel_popup(f"Port {port} already in use by {client_using.name}, \
                                                 auto reassign port for {client_using.name}?")
            if result == "Cancel":
                return
            else:
                client_using.change_port(self.Session.find_empty_port())
                client.change_port(port)

    # main GUI update loop
    def event_loop(self):

        while True:
            
            event, values = self.window.read(timeout=300)

            if event == "Exit" or event == sg.WIN_CLOSED:
                self.Session.deactivate_all()
                break

            # update main listbox, return activeClient and check if changed selection
            activeClient, selectionChanged = self.update_client_listboxbox(values)

            if event == "_create":
                self.Session.create_client(
                    name=values["_name"],
                    portOffset=None, # automatically assigned if None
                    channels=values["_create_num_ch"],
                    autoConnectAudio=True,
                    zeroUnderrun=True,
                    autoManage=values['_automanage'])
            
            if event == '_load_sess':
                self.Session.load_session(self.file_browser())

            if activeClient is not None:

                if event == '_remove':
                    self.Session.delete_client(activeClient)
                if event == '_activate_all':
                    self.Session.activate_all()
                if event == '_deactivate_all':
                    self.Session.deactivate_all()
                if event == '_save_sess':
                    self.Session.save_session(self.folder_browser())
                if event == '_change_name':
                    text = self.text_entry("Name Entry")
                    activeClient.name = self.Session.crosscheck_name(text)
                if event == '_change_port':
                    port = self.text_entry("Enter a new port")
                    self.port_change(port, activeClient)
                # if event == '_automan_client':
                activeClient.autoManage = values['_automan_client']



                self.update_client_pane(activeClient, event, selectionChanged)
            else:
                self.display_empty_client()

        self.window.close()