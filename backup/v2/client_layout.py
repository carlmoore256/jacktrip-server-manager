import PySimpleGUI as sg

title_col = [
    [sg.Text("Name:", size=(12,1)),
    sg.Text(size=(15,1), key="-ACTIVE_NAME-")]
]

client_viewer_contents = [
    # [sg.Column(title_col)],
    [sg.Text('Status:'), sg.Text('NOT CONNECTED', key='-CONNECT_STATUS-')],
    [sg.Text('Port Offset: '), sg.Text('', key='-C_PORT_OFS-')],
    [sg.Text('Channels:'), sg.Text('', key='-C_NUM_CHAN-')],
    [sg.Button('Disable', key="-CHANGE_ACTIVE-", button_color=('black', 'red'))],
    [sg.Button('Remove', key="-DELETE_CLIENT-")],
    #---------CONSOLE----------#
    [sg.MLine(key='-ML1-'+sg.WRITE_ONLY_KEY, size=(40,8), autoscroll=True)],
    [sg.Text(size=(40,1), key='-LINE-OUTPUT-')],
]

# listbox has right_click_menu parameter, implement this

client_viewer_frame = [
    [sg.Frame('Default Client',
    layout=client_viewer_contents,
    font='Any 12',
    key="-CLIENT_FRAME-")]
]
