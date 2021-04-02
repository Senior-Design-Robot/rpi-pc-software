import socket
import socketserver

SERV_HOST, SERV_PORT = "0.0.0.0", 1896
ESP_PORT = 1897


class HandlerEspPacket(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024)
        print(self.data)


def init_server():
    tcp_server = socketserver.TCPServer((SERV_HOST, SERV_PORT), HandlerEspPacket)
    tcp_server.serve_forever()


def send_bytes(sck: socket.socket, bytes_to_send, to_send):
    total_sent = 0

    while total_sent < to_send:
        sent = sck.send(bytes_to_send[total_sent:])
        if sent == 0:
            print("Connection broken")
            return

        total_sent += sent

