import PySimpleGUI as sg

title_col = [
    [sg.Text("Name:", size=(12,1)),
    sg.Text(size=(15,1), key="-ACTIVE_NAME-")]
]

client_viewer_contents = [
    [sg.Column(title_col)],
    [sg.Text('Status:'), sg.Text('NOT CONNECTED')],
    [sg.Text('Channels:'), sg.Text('', key='-C_NUM_CHAN-')],
    [sg.Text('Port Offset: '), sg.Text('', key='-C_PORT_OFS-')],
    [sg.Button('Disable', key="-CHANGE_ACTIVE-")],
    [sg.Button('Remove', key="-DELETE_CLIENT-")],
    #---------CONSOLE----------#
    # [sg.Output(size=(40,6))],
    [sg.Text(size=(40,1), key='-LINE-OUTPUT-')],
]


client_viewer_frame = [
    [sg.Frame('Default Client',
    layout=client_viewer_contents,
    key="-CLIENT_FRAME-")]
]
