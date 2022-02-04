import socket
import sqlite3
import ssl

HOST = '127.0.0.1'
PORT = 65432

conn = sqlite3.connect('Users.db')
c = conn.cursor()


def Register(username, password,sock):
    global conn
    global c
    c.execute("CREATE TABLE IF NOT EXISTS users (username NVARCHAR(16) NOT NULL PRIMARY KEY, password NVARCHAR(32) NOT NULL ) ")
    c.execute("SELECT * FROM users where username = '%s'"%(username))
    if c.fetchone():
        sock.write("Username is taken".encode())
    else:
        try:

            c.execute("INSERT INTO users VALUES ('%s','%s')" %(username, password))
            conn.commit()
            sock.write("Registered Successfully".encode())
        except Exception as exe:
            sock.write("An Error has occurred".encode())
            print(exe)

def Login(username,password,sock):
    global conn
    global c
    c.execute("SELECT * FROM users where username ='%s' AND password = '%s'"%(username,password))
    if c.fetchone():

        sock.write("Successful Login".encode())

    else:
        sock.write("Wrong username or password, try again.".encode())




if __name__ == '__main__':

    CERT = "key_cert_.pem"
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT)
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                connection, addr = s.accept()
                with context.wrap_socket(connection,server_side=True) as ssl_connection:
                    print('Connected by', addr)
                    while True:
                        data = ssl_connection.recv(1024)
                        if not data:
                            break
                        else:
                            data = data.decode()
                            if data.startswith('register:'):
                                username = data.split(":")[1]
                                password = data.split(":")[2]
                                Register(username,password,ssl_connection)
                            elif data.startswith('login:'):
                                username = data.split(":")[1]
                                password = data.split(":")[2]
                                Login(username, password, ssl_connection)

        except Exception as exe:
            print("ERROR : "+str(exe))




