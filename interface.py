import client_layout

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
                sg.Checkbox('AutoManage', default=True, key='_automanage')
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
    def update_client_listboxbox(self):
        selIndex = self.window['_client_listbox'].get_indexes()
        if len(selIndex) > 0:
            self.selectedClient = selIndex[0]
        status_labels = self.Session.client_label_status()
        self.window["_client_listbox"].update(status_labels, set_to_index=self.selectedClient)

    # updates client information display (right side)
    def update_client_pane(self, client, event):
        self.window['_console_line'].update(client.currentOutput)
        self.window['_console_scroll' + sg.WRITE_ONLY_KEY].print(f'{client.currentOutput}\n', end='')
        self.window["_client_frame"].update(client.name)
        self.window['_num_ch'].update(client.channels)
        self.window['_offset'].update(client.portOffset)

        if client.connectionActive:
            self.window['_connect_status'].update('Connected', text_color='white')
            self.window['_quality_label'].update('{:10.2f}'.format(client.connectionQuality))
            self.window['_skew'].update(str(client.skew))
        else:
            self.window['_connect_status'].update('Not Connected', text_color='red')
            self.window['_quality'].update('-')
            self.window['_skew'].update('-')

        if event == '_change_active':
            if client.isActive:
                client.kill_server_thread()
                self.window['_change_active'].update('Enable')
                self.window['_change_active'].Update(button_color=('black', 'green'))
            else:
                client.run_server_thread()
                self.window['_change_active'].update('Disable')
                self.window['_change_active'].Update(button_color=('black', 'red'))

        if client.connectionQuality > 0.5:
            self.window['_quality'].update('GOOD', text_color='yellow')
        else:
            self.window['_quality'].update('UNSTABLE', text_color='red')

    def file_browser(self):
        filepath = sg.popup_get_file('Select session file')
        return filepath

    def folder_browser(self):
        filepath = sg.popup_get_folder('Select save directory')
        return filepath

    # main GUI update loop
    def event_loop(self):

        while True:
            
            event, values = self.window.read(timeout=300)

            if event == "Exit" or event == sg.WIN_CLOSED:
                self.Session.deactivate_all()
                break

            if len(values['_client_listbox']) > 0:
                clientName = values["_client_listbox"][0][2:]
                
                # if clientName != self.selectedClient: # check if selection changed
                activeClient = self.Session.client_by_name(clientName)
                    # self.selectedClient = clientName
            else:
                activeClient = None

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
                elif event == '_activate_all':
                    self.Session.activate_all
                elif event == '_deactivate_all':
                    self.Session.deactivate_all()
                elif event == '_save_sess':
                    self.Session.save_session(self.folder_browser())


                self.update_client_pane(activeClient, event)
            else:
                self.display_empty_client()
            self.update_client_listboxbox()

            
        self.window.close()