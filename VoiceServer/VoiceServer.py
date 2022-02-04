import socket
import threading


class Server:
    def __init__(self):
        self.ip = '127.0.0.1'
        while 1:
            try:
                self.MainPort = 55565
                self.updatePort = 55575



                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.bind((self.ip, self.MainPort))
                self.updateSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.updateSock.bind((self.ip, self.updatePort))
                break
            except:
                print("Couldn't bind to that port")

        self.connections = []
        self.nicknames = []
        self.updateConnections=[]

        self.muted = []

        self.admins = []
        self.updateAdmins()

        self.accept_connections()


    def isAdmin(self,nickname):
        if nickname in self.admins:
            return True
        return False

    def updateAdmins(self):
        o = open("Admins.txt",'r')
        text = o.read()
        admins = text.split(",")
        for i in admins:
            self.admins.append(i)

    def accept_connections(self):
        self.s.listen()
        self.updateSock.listen()
        print('Running on IP: ' + self.ip)
        print('Running on port: ' + str(self.MainPort))
        try:
            while True:
                c, addr = self.s.accept()
                d, addr1 = self.updateSock.accept()
                nickname = c.recv(1024).decode()
                self.updateConnections.append((d,nickname))
                self.connections.append((c,nickname))
                self.nicknames.append(nickname)
                self.updateClients()
                print(self.nicknames)
                threading.Thread(target=self.handle_client, args=(c, addr)).start()
                threading.Thread(target=self.receiveCommands,args=(d,addr1)).start()
        except Exception as exe:
            print(exe)

    def broadcast(self, sock, data):
        for client in self.connections:
            if client[0] != self.s and client[0] != sock:
                try:
                    client[0].send(data)
                except:
                    pass

    def getConn(self,nickname):
        for i in self.updateConnections:
            if i[1] == nickname:
                return i[0]
        return


    def kick(self,nickname):
        for i in self.connections:
            if i[1] == nickname:
                print(str(nickname)+" has Been Kicked")
                conn = self.getConn(nickname)
                conn.send("kicked".encode())
                conn.close()
                i[0].close()



    def receiveCommands(self, d, addr):
        while 1:
            try:
                data = d.recv(1024).decode()
                if data.startswith("mute:"):
                    nickname = data.split(":")[1].replace(" ","")
                    sentby = data.split(":")[2].replace(" ","")
                    if self.isAdmin(sentby):
                        if nickname in self.muted:
                            self.muted.remove(nickname)
                            print("Unmuted : "+ str(nickname))
                        else:
                            self.muted.append(nickname)
                            print("Muted : " + str(nickname))
                elif data.startswith("kick:"):
                    nickname = data.split(":")[1].replace(" ", "")
                    sentby = data.split(":")[2].replace(" ", "")
                    if self.isAdmin(sentby):
                        self.kick(nickname)


            except socket.error:
                break

    def updateClients(self):
        for client in self.updateConnections:
            if client[0] != self.s:
                try:
                    data = str(self.nicknames)
                    client[0].send(data.encode())

                except:
                    pass

    def isMuted(self,c):
        for i in self.connections:
            if i[0] == c:
                if i[1] in self.muted:
                    return True
        return False

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                if self.isMuted(c):
                    pass
                else:
                    self.broadcast(c, data)

            except socket.error:
                for i in self.connections:
                    if i[0] == c:
                        for j in self.updateConnections:
                            if j[1] == i[1]:
                                j[0].close()
                                self.updateConnections.remove(j)


                        self.connections.remove(i)
                        self.nicknames.remove(i[1])
                        self.updateClients()
                c.close()
                break


server = Server()
