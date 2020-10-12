import PySimpleGUI as sg

title_col = [
    [sg.Text("Name:", size=(12,1)),
    sg.Text(size=(15,1), key="-ACTIVE_NAME-")]
]

client_viewer_contents = [
    # [sg.Column(title_col)],
    [sg.Text('Status:'), sg.Text('NOT CONNECTED', key='-CONNECT_STATUS-')],
    [sg.Text('Quality:'), sg.Text('-', key='-C_QUALITY-')],
    [sg.Text('Rating:'), sg.Text('-', size=(12,1), key='-C_QUALITY_RATING-')],
    [sg.Text('Skew:'), sg.Text('-', key='-C_SKEW-')],
    [sg.Text('Port Offset:'), sg.Text('', key='-C_PORT_OFS-')],
    [sg.Text('Channels:'), sg.Text('', key='-C_NUM_CHAN-')],
    [sg.Button('Disable', key="-CHANGE_ACTIVE-", button_color=('black', 'red'))],
    [sg.Button('Remove', key="-DELETE_CLIENT-")],
    #---------CONSOLE----------#
    [sg.MLine(key='-ML1-'+sg.WRITE_ONLY_KEY, size=(40,8), autoscroll=True)],
    [sg.Text(size=(40,1), key='-LINE-OUTPUT-')],
]

# listbox has right_click_menu parameter, implement this

client_viewer_frame = [
    [sg.Frame('[Create or select a client]',
    layout=client_viewer_contents,
    font='Any 12',
    key="-CLIENT_FRAME-")]
]

def reset_view(window):
    window['-CONNECT_STATUS-'].update('-')
    window['-C_QUALITY-'].update('-')
    window['-C_QUALITY_RATING-'].update('-')
    window['-C_NUM_CHAN-'].update('-')
    window['-CHANGE_ACTIVE-'].update(button_color=('gray', 'white'))


        # window[]
