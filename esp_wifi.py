import enum
import socket
import socketserver
from typing import Tuple, List

SERV_HOST, SERV_PORT = "0.0.0.0", 1896
ESP_PORT = 1897

UINT32_MAX = 4294967295


class WPacketType(enum.IntEnum):
    WPKT_NULL = 0
    WPKT_SETTING = 1
    WPKT_POINTS = 2


class PathElementType(enum.IntEnum):
    PATH_NONE = 0
    PATH_MOVE = 1
    PATH_PEN_UP = 2
    PATH_PEN_DOWN = 3


WPKT_HEAD_LEN = 5
WPKT_SETTING_LEN = (WPKT_HEAD_LEN + 2)
WPKT_POINTS_LEN = (WPKT_HEAD_LEN + 1)

WFIELD_PKT_TYPE = 4
WFIELD_SETTING_ID = 5
WFIELD_SETTING_VAL = 6

WFIELD_N_PTS = 5
WFIELD_POINTS = 6

WPOINT_LEN = 9
WPOINT_X_OFFSET = 1
WPOINT_Y_OFFSET = 5


class HandlerEspPacket(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024)
        print(self.data)


def init_server():
    tcp_server = socketserver.TCPServer((SERV_HOST, SERV_PORT), HandlerEspPacket)
    tcp_server.serve_forever()


def apply_header(pkt: bytearray, pkt_type: WPacketType):
    pkt[0] = 0xFF
    pkt[1] = 0xFF
    pkt[2] = 0xFD
    pkt[3] = 0
    pkt[WFIELD_PKT_TYPE] = pkt_type.value


def write_packet_xy(pkt: bytearray, offset: int, val: float):
    # values are stored 32 bit fraction, MSB first
    int_val = int(round(val * UINT32_MAX))

    for i in range(3, -1, -1):
        pkt[offset + i] = int_val & 0xFF
        int_val >>= 8


def create_points_pkt(pt_list: List[Tuple[PathElementType, float, float]]) -> bytes:
    n_pts = len(pt_list)
    pkt_len = WPKT_POINTS_LEN + (n_pts * WPOINT_LEN)
    pkt = bytearray(pkt_len)

    apply_header(pkt, WPacketType.WPKT_POINTS)

    for i in range(0, n_pts):
        p_type, x, y = pt_list[i]
        pt_offset = i * WPOINT_LEN

        pkt[pt_offset] = p_type.value
        write_packet_xy(pkt, pt_offset + WPOINT_X_OFFSET, x)
        write_packet_xy(pkt, pt_offset + WPOINT_Y_OFFSET, y)

    return pkt


def send_bytes(sck: socket.socket, bytes_to_send, to_send):
    total_sent = 0

    while total_sent < to_send:
        sent = sck.send(bytes_to_send[total_sent:])
        if sent == 0:
            print("Connection broken")
            return

        total_sent += sent

