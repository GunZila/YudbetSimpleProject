from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QGridLayout, QApplication, QLabel
from PyQt5.QtGui import QIcon, QPixmap
import socket
import threading
import pyaudio


class Ui_MainWindow(QWidget):
    def __init__(self, targetip, nickname):
        super().__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Audio socket
        self.d = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # info socket
        self.target_ip = targetip
        self.nickname = nickname
        self.window2 = QtWidgets.QMainWindow()
        self.setupUi(self.window2)
        self.OnlineUsers = []
        self.stopthreads = False

        while 1:
            try:
                self.target_port = 55565
                self.updateport = 55575
                self.s.connect((self.target_ip, self.target_port))
                self.d.connect((self.target_ip, self.updateport))

                break
            except:
                print("Couldn't connect to server, Retrying...")
        self.s.send(nickname.encode())
        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

        print("Connected to Server")

        # start threads
        receive_audio = threading.Thread(target=self.receive_server_data).start()
        receive_Online = threading.Thread(target=self.receiveOnline).start()
        send_data = threading.Thread(target=self.send_data_to_server).start()


    def receiveOnline(self):
        while True:
            if self.stopthreads == True:
                break
            try:
                data = self.d.recv(1024)
                info = data.decode()
                if info.startswith("kicked"):
                    print("You got kicked, you can now close this window.")
                    self.gotKicked()
                    self.stopthreads = True
                    pixmap = QPixmap("kicked.png")
                    self.User_list.setPixmap(pixmap)

                else:
                    userlist = info[2:len(info) - 2].replace("'", "")
                    self.OnlineUsers = userlist.split(",")
                    self.UpdateScreen()
            except Exception as exe:
                print(exe)

    def gotKicked(self):
        for i in range(self.layout.count(),1,-1):
            self.layout.itemAt(i-1).widget().deleteLater()






    def UpdateScreen(self):
        self.delButton.click()
        self.addButton.click()

    def receive_server_data(self):
        while True:
            if self.stopthreads == True:
                break
            try:
                data = self.s.recv(1024)
                try:
                    info = data.decode()

                except Exception as exe:
                    self.playing_stream.write(data)
            except:
                pass

    def send_data_to_server(self):
        while True:
            if self.stopthreads == True:
                break
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except:
                pass

    def setupUi(self, MainWindow):

        self.addButton = QPushButton("add")
        self.addButton.clicked.connect(self.add)

        self.delButton = QPushButton("delete")
        self.delButton.clicked.connect(self.delete)

        self.layout = QGridLayout()

        self.User_list = QLabel()

        pixmap = QPixmap("choice.png")
        self.User_list.setPixmap(pixmap)
        self.resize(400, 600)
        self.setMaximumSize(400, 800)
        self.layout.addWidget(self.User_list, 0, 0)


        self.setLayout(self.layout)

        self.setWindowTitle('As Usual')
        self.show()

    def add(self):
        try:
            for i in range(len(self.OnlineUsers)):
                font = QtGui.QFont()
                font.setFamily("Guttman Yad-Brush")
                font.setPointSize(24)
                font.setBold(True)
                name = str(self.OnlineUsers[i])
                Button = QPushButton(name)
                Button.setFont(font)
                Button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
                Button.clicked.connect(self.sendMuteCommand)
                self.layout.addWidget(Button, i + 2, 0)
                kickButton = QPushButton("Kick")
                kickButton.setObjectName(name)
                kickButton.clicked.connect(self.sendKickCommand)
                self.layout.addWidget(kickButton, i + 2, 1)
        except Exception as error:
            print(error)

    def sendKickCommand(self):

        nickname = self.sender().objectName()

        try:
            if not nickname == self.nickname:
                data = "kick:" + str(nickname) + ":" + str(self.nickname)
                self.d.send(data.encode())

        except Exception as exe:
            print(exe)

    def sendMuteCommand(self):
        nickname = self.sender().text()

        try:
            data = "mute:" + str(nickname) + ":" + str(self.nickname)
            self.d.send(data.encode())
        except Exception as exe:
            print(exe)

    def delete(self):
        for i in range(self.layout.count() - 3):
            self.layout.itemAt(i + 3).widget().deleteLater()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow("127.0.0.1", "Client")
    sys.exit(app.exec_())
