import PySimpleGUI as sg

title_col = [
    [sg.Text("Name:", size=(12,1)),
    sg.Text(size=(15,1), key="-ACTIVE_NAME-")]
]

client_viewer_contents = [
    # [sg.Column(title_col)],
    [sg.Text('Status:'), sg.Text('NOT CONNECTED', key='_connect_status')],
    [sg.Text('Quality:'), sg.Text('-', key='_quality')],
    [sg.Text('Rating:'), sg.Text('-', size=(12,1), key='_quality_label')],
    [sg.Text('Skew:'), sg.Text('-', key='_skew')],
    [sg.Text('Port Offset:'), sg.Text('', key='_offset')],
    [sg.Text('Channels:'), sg.Text('', key='_num_ch')],
    [sg.Button('Disable', key="_change_active", button_color=('black', 'red'))],
    [sg.Button('Remove', key="_remove")],
    #---------CONSOLE----------#
    [sg.MLine(key='_console_scroll'+sg.WRITE_ONLY_KEY, size=(40,8), autoscroll=True)],
    [sg.Text(size=(40,1), key='_console_line')],
]

# listbox has right_click_menu parameter, implement this

client_viewer_frame = [
    [sg.Frame('[Create or select a client]',
    layout=client_viewer_contents,
    font='Any 12',
    key="_client_frame")]
]

# def reset_view(window):
#     window['_connect_status'].update('-') 
#     window['_quality'].update('-')
#     window['_quality_label'].update('-')
#     window['_num_ch'].update('-')
#     window['_change_active'].update(button_color=('gray', 'white'))
