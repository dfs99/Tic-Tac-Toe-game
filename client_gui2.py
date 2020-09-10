import wx
import socket
import threading


HEADERSIZE = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECTED = 'disconnected'
# pass my ip in order to allow others to connect to it in my local network
SERVER = "192.168.1.42"
ADDR = (SERVER, PORT)
TOKEN = 'O'

# it will allow the player to make its move
data_received = [2, "True"]
# board instance in order to access it
class_board_instance = ''


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def place_enemy_player_token():
    coordinates = data_received[0].split('-')
    pos_x = int(coordinates[0])
    pos_y = int(coordinates[1])
    global class_board_instance
    for row in class_board_instance.board:
        for cell in row:
            if (cell.pos_x == pos_x) and (cell.pos_y == pos_y):
                if cell.button.GetName() == "player2":
                    pass
                else:
                    # X
                    cell.button.SetLabel('X')
                    cell.button.SetName('player1')
                    cell.is_filled = True


def receive_data():
    while True:
        data = client.recv(2048).decode(FORMAT)
        if data:
            print("[DATA has been successfully received]")
            print(data)
            global data_received
            for elem in data_received:
                data_received.remove(elem)
            # del data_received
            data_received = data.split(' ')
            place_enemy_player_token()


def send(msg):

    print("[STARTING SENDING DATA]")
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADERSIZE - len(send_length))
    client.send(send_length)
    client.send(message)


class Cell(wx.Button):

    def __init__(self, pos_x, pos_y, parent, *args, **kw):
        super().__init__(*args, **kw)
        self._button = wx.Button(parent, label='', size=(150, 150), name='')
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._is_filled = False

    @property
    def pos_x(self):
        return self._pos_x

    @property
    def pos_y(self):
        return self._pos_y

    @property
    def button(self):
        return self._button

    @property
    def is_filled(self):
        return self._is_filled

    @is_filled.setter
    def is_filled(self, value=True):
        self._is_filled = value


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='TIC TAC TOE game', size=(500, 515),
                         style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        # sizer to contain the panels
        self.vertical_box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vertical_box_sizer)

        # create the first panel to contain the game menu
        panel = Menu(self)
        # add the panel to the frames sizer
        # wx.ALL adds a border on all sides of the widget
        # wx.EXPAND makes the panel to expand itself as much as they can within the sizer
        self.vertical_box_sizer.Add(panel, wx.ID_ANY, wx.EXPAND | wx.ALL, 10)
        # it centres the window
        self.Centre()


class Menu(wx.Panel):

    def __init__(self, parent):
        self.frame_instance = parent
        super(Menu, self).__init__(self.frame_instance)

        self.SetBackgroundColour('GREY')
        vertical_box_sizer = wx.BoxSizer(wx.VERTICAL)

        self.play_button = wx.Button(self, label='PLAY')
        self.exit_button = wx.Button(self, label='EXIT')
        vertical_box_sizer.Add(self.play_button, wx.ID_ANY, wx.EXPAND | wx.ALL, 75)
        vertical_box_sizer.Add(self.exit_button, wx.ID_ANY, wx.EXPAND | wx.ALL, 75)
        self.play_button.Bind(wx.EVT_LEFT_DOWN, self.end_introduction)
        self.exit_button.Bind(wx.EVT_LEFT_DOWN, self.shut_down_game)
        self.SetSizer(vertical_box_sizer)
        self.Centre()

    def end_introduction(self, event):
        """ method to close the first window where the menu is set up """
        # create the panel for the board
        board = Board(self.frame_instance)
        # replace the panel in the frame sizer
        self.frame_instance.vertical_box_sizer.Replace(self, board)
        # redraw the panel to avoid errors
        self.frame_instance.Layout()
        # delete the former panel
        self.Destroy()

    def shut_down_game(self, event):
        self.frame_instance.Close()


class Board(wx.Panel):
    __turn = 0

    def __init__(self, parent):
        self.frame_instance = parent
        super(Board, self).__init__(self.frame_instance)

        # Create the GridSizer to use with the Panel
        grid = wx.GridSizer(3, 3, 5, 5)
        # create the cells
        self.button_list = []
        # create a list[list[Cell]] in order to be easier to check all the cells
        self.board = [[Cell(i, j, self) for j in range(0, 3)] for i in range(0, 3)]
        # in order to have outer access to it for depict the other player
        global class_board_instance
        class_board_instance = self
        # fulfill the button_list
        for row in self.board:
            for cell in row:
                self.button_list.append(cell)
        # set up the event in order to place the token in each cell
        [self.button_list[i].button.Bind(wx.EVT_LEFT_DOWN, self.set_token) for i in range(0, 9)]

        # add the widgets to the sizer - add the button attribute of class cell
        grid.AddMany([self.button_list[0].button, self.button_list[1].button, self.button_list[2].button,
                      self.button_list[3].button, self.button_list[4].button, self.button_list[5].button,
                      self.button_list[6].button, self.button_list[7].button, self.button_list[8].button])

        # Set the sizer on the panel
        self.SetSizer(grid)

    def is_board_full(self):
        count = 0
        for row in self.board:
            for cell in row:
                # print(cell.pos_x, cell.pos_y, cell.button.GetName())
                if (cell.button.GetName() != '') is True:
                    count += 1
        if count == 9:
            return True
        return False

    def end_game(self):
        if self.is_board_full() is True:
            dialog = wx.MessageDialog(None, message="Game over, it's a draw.", style=wx.OK)
            dialog.ShowModal()
            # shut down the panel and set up again the menu panel
            self.frame_instance.vertical_box_sizer.Replace(self, Menu(self.frame_instance))
            self.frame_instance.Layout()
            self.Destroy()

    def set_token(self, event):

        global data_received
        if data_received[1] == "False":

            button = event.GetEventObject()
            if button.GetName() == '':
                # if the board is not full
                if self.is_board_full() is False:
                    button.SetLabel('O')
                    button.SetName('player2')
                    # mark the cell to filled
                    for row in self.board:
                        for cell in row:
                            if cell.button is button:
                                cell.is_filled = True
                                cell_filled = cell
                    self.__turn += 1

                # send the data
                player_turn = "True"
                thread = threading.Thread(target=send, args=(f'{cell_filled.pos_x}-{cell_filled.pos_y} {player_turn}',))
                thread.daemon = True
                thread.start()

                # check whether there is a winner or not
                self.is_a_win()
                # if no winner, end the game
                self.end_game()
            else:
                dialog = wx.MessageDialog(None,
                                          message='You cannot place your token here, the cell is already filled up.',
                                          style=wx.OK)
                dialog.ShowModal()

        else:
            dialog = wx.MessageDialog(None,
                                      message="Wait your turn, it's the other player's turn",
                                      style=wx.OK)
            dialog.ShowModal()

    def is_a_win(self):
        win_row_p1 = self.check_rows(self.board, 'player1', 0)
        win_column_p1 = self.check_columns(self.board, 'player1', 0)
        win_cross_left_p1 = self.check_crosses_left(self.board, 'player1')
        win_cross_right_p1 = self.check_crosses_right(self.board, 'player1')

        win_row_p2 = self.check_rows(self.board, 'player2', 0)
        win_column_p2 = self.check_columns(self.board, 'player2', 0)
        win_cross_left_p2 = self.check_crosses_left(self.board, 'player2')
        win_cross_right_p2 = self.check_crosses_right(self.board, 'player2')

        # check which player has won
        if win_row_p1 is True or win_column_p1 is True or win_cross_left_p1 is True or win_cross_right_p1 is True:
            # finish the game, player 1 has won
            dialog = wx.MessageDialog(None, message='Congratulations player1', style=wx.OK)
            dialog.ShowModal()
            # in order to disconnect the client
            disconnect_thread = threading.Thread(target=send, args=("disconnectclient",))
            disconnect_thread.daemon = True
            disconnect_thread.start()
            # shut down the panel and set up again the menu panel
            self.frame_instance.vertical_box_sizer.Replace(self, Menu(self.frame_instance))
            self.frame_instance.Layout()
            self.Destroy()

        elif win_row_p2 is True or win_column_p2 is True or win_cross_left_p2 is True or win_cross_right_p2 is True:
            # finish the game, player 2 has  won
            dialog = wx.MessageDialog(None, message='Congratulations player2', style=wx.OK)
            dialog.ShowModal()
            # in order to disconnect the client
            disconnect_thread = threading.Thread(target=send, args=("disconnectclient",))
            disconnect_thread.daemon = True
            disconnect_thread.start()
            # shut down the panel and set up again the menu panel
            self.frame_instance.vertical_box_sizer.Replace(self, Menu(self.frame_instance))
            self.frame_instance.Layout()
            self.Destroy()

    @staticmethod
    def check_rows(board, value, index_count):
        win = False
        while index_count < 3:
            win_counter = 0
            for row in board:
                for cell in row:
                    if cell.pos_x == index_count:
                        if cell.button.GetName() == value:
                            win_counter += 1
            if win_counter == 3:
                win = True
                index_count = 9
            index_count += 1
        return win

    @staticmethod
    def check_columns(board, value, index_count):
        win = False
        while index_count < 8:
            win_counter = 0
            for row in board:
                for cell in row:
                    if cell.pos_y == index_count:
                        if (cell.button.GetName() == value) is True:
                            win_counter += 1
            if win_counter == 3:
                win = True
                index_count = 9
            index_count += 1
        return win

    @staticmethod
    def check_crosses_left(board, value):
        win_counter = 0
        for row in board:
            for cell in row:
                if cell.pos_x + cell.pos_y == 2:
                    if (cell.button.GetName() == value) is True:
                        win_counter += 1
        if win_counter == 3:
            return True
        return False

    @staticmethod
    def check_crosses_right(board, value):
        win_counter = 0
        for row in board:
            for cell in row:
                if cell.pos_x - cell.pos_y == 0:
                    if (cell.button.GetName() == value) is True:
                        win_counter += 1
        if win_counter == 3:
            return True
        return False


class MainApp(wx.App):
    def OnInit(self):
        """Initialise the main GUI Application"""
        frame = MainFrame()
        frame.Show()
        thread1 = threading.Thread(target=receive_data)
        thread1.daemon = True
        thread1.start()
        # indicate whether the processing should continue or not
        return True


# Run the GUI application
# create the application object
app = MainApp()
# start the event loop
app.MainLoop()
