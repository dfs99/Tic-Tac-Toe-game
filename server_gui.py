import socket
import threading
import wx

HEADERSIZE = 67
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECTED = 'disconnectclient'
client_list = []
# it contains all the data shared between the clients
all_msgs = ""

# ipv4 & TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# It allows the server to be started again, once it has been run the close func
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def handle_client(conn, addr):
    """it will handle all the communication between the server and the clients"""
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True

    while connected:
        # wait to receive connection from the client
        # The first msg tells us how long the msg is, so we'll convert into an integer
        msg_length = conn.recv(HEADERSIZE).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            # we'll receive the actual msg with the exactly length
            msg = conn.recv(msg_length).decode(FORMAT)
            global all_msgs
            all_msgs = all_msgs + msg + " "
            if msg == DISCONNECTED:
                connected = False
            print(f'[{addr}] {msg}')
            # send back a msm to the client from the server
            for client in client_list:
                client.send(msg.encode(FORMAT))
    conn.close()


def start(server_window_instance):
    global server
    server.bind(ADDR)

    # print out the data in the panel
    msg = "[STARTING] server is starting... \n"
    server_window_instance.stdout.SetLabel(msg)
    print('[STARTING] server is starting... ')

    server.listen(1)
    msg = msg + f'[LISTENING] Server is listening on {SERVER} \n'
    server_window_instance.stdout.SetLabel(msg)
    print(f'[LISTENING] Server is listening on {SERVER}')

    thread = threading.Thread(target=accept_clients, args=(server, server_window_instance), daemon=True)
    thread.daemon = True
    thread.start()

    msg = msg + "[ACCEPTING NEW CLIENTS TO THE SERVER]\n" + ' ' + '*'*59 + '\n'
    server_window_instance.stdout.SetLabel(msg)
    print("[ACCEPTING NEW CLIENTS TO THE SERVER]")

    server_window_instance.host_info_text.SetLabel(str(SERVER))
    server_window_instance.port_info_text.SetLabel(str(PORT))


def accept_clients(server, server_windows_instance):

    while True:
        # conn: it stores the socket object that allow us to send back information
        # addr: information about the connection
        conn, addr = server.accept()
        client_list.append(conn)
        # create another thread to avoid the blockers to stop the GUI main loop
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()
        msg = server_windows_instance.stdout.GetLabel()
        msg = msg + f'[ACTIVE CONNECTIONS] {threading.active_count() - 2}\n'
        server_windows_instance.stdout.SetLabel(msg)
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 2}')


def close(server_window_instance):
    """modo chapuza, no va del tod0 bien"""

    global server
    # server.shutdown(socket.SHUT_RDWR)

    server.close()
    msg = server_window_instance.stdout.GetLabel()
    msg = msg + "[SERVER CLOSED]\n"
    server_window_instance.stdout.SetLabel(msg)
    print('SERVER CLOSED')

    server_window_instance.host_info_text.SetLabel('___.___.___.___')
    server_window_instance.port_info_text.SetLabel('_______')


class ServerWindow(wx.Frame):

    def __init__(self):
        super(ServerWindow, self).__init__(parent=None, title='SERVER', size=(337, 400),
                                           style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        # font for the frame of 15px
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(15)

        # set up the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # create the sizer for the first row
        first_row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # create its widgets
        self.conn_button = wx.Button(self, label='Connect')
        self.conn_button.Bind(wx.EVT_LEFT_DOWN, self.connect_server)
        self.stop_button = wx.Button(self, label='Stop')
        self.stop_button.Bind(wx.EVT_LEFT_DOWN, self.stop_server)
        # add widgets to the panel
        first_row_sizer.Add(self.conn_button, flag=wx.ALIGN_CENTRE | wx.ALL, border=10)
        first_row_sizer.Add(self.stop_button, flag=wx.ALIGN_CENTRE | wx.ALL, border=10)

        # create the sizer for the second row
        second_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # create its widgets
        self.host_text = wx.StaticText(self, wx.ID_ANY, label='Host:')
        self.host_text.SetFont(font)
        self.host_info_text = wx.StaticText(self, wx.ID_ANY, label='___.___.___.___')
        self.port_text = wx.StaticText(self, wx.ID_ANY, label='Port:')
        self.port_text.SetFont(font)
        self.port_info_text = wx.StaticText(self, wx.ID_ANY, label='_______')
        # add widgets to the sizer
        second_row_sizer.Add(self.host_text, flag=wx.RIGHT, border=15)
        second_row_sizer.Add(self.host_info_text, flag=wx.ALIGN_CENTRE | wx.RIGHT, border=15)
        second_row_sizer.Add(self.port_text, flag=wx.LEFT, border=15)
        second_row_sizer.Add(self.port_info_text, flag=wx.ALIGN_CENTRE | wx.LEFT, border=15)

        # third row
        name = ' ' + '*'*28 + 'Clients' + '*'*28
        self.client_text = wx.StaticText(self, wx.ID_ANY, label=name)

        # the fourth row will be a panel to display data
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('white')
        self.stdout = wx.StaticText(self.panel, wx.ID_ANY, label='')

        # Add all the rows to the first sizer
        main_sizer.Add(first_row_sizer, flag=wx.ALIGN_CENTER, border=15)
        main_sizer.Add(second_row_sizer, flag=wx.ALIGN_CENTER, border=15)
        main_sizer.Add(self.client_text, flag=wx.ALIGN_CENTER, border=5)
        main_sizer.Add(self.panel, wx.ID_ANY, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def connect_server(self, e):
        """connect the server"""
        start(self)

    def stop_server(self, e):
        """disconnect the server"""
        close(self)


app = wx.App(False)
frame = ServerWindow()
frame.Show()
app.MainLoop()
