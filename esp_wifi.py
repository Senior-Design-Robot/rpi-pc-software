import enum
from typing import Tuple, List

from PyQt5.QtCore import pyqtSlot, QObject, Qt
from PyQt5.QtNetwork import QTcpSocket

import esp_status as esp

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


class EspSetting(enum.IntEnum):
    MODE = 1
    SPEED = 2


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

POINT_TARGET_FILL = 31
POINT_XMIT_THRESHOLD = 16


class TransmitWrapper(QObject):
    @pyqtSlot()
    def on_connected(self):
        self.socket.write(self.data)

    @pyqtSlot('qint64')
    def on_write(self, n_bytes):
        self.bytes_sent += n_bytes
        print(f"{n_bytes} written to {self.socket.peerAddress().toString()}")

        if self.bytes_sent >= self.send_length:
            self.socket.close()
            self.deleteLater()

    @pyqtSlot()
    def on_error(self):
        print(f"Error occurred while sending data to {self.socket.peerAddress().toString()}:\
            {self.socket.errorString()}")

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.on_connected)
        self.socket.errorOccurred.connect(self.on_error)
        self.socket.bytesWritten.connect(self.on_write)

        self.data = None
        self.bytes_sent = 0
        self.send_length = 0

    def start_transmit(self, address, data: bytes):
        self.data = data
        self.send_length = len(data)
        self.socket.connectToHost(address, ESP_PORT)


def handle_packet(data: bytes, address: str, dev_table: esp.DeviceTable):
    print(data)

    data_str = data.decode('ascii')
    fields = data_str.split(',')

    # 0     1       2         3     4              5           6         7
    # type, dev ID, pwr good, mode, shoulder stat, elbow stat, odometer, pts left

    if len(fields) == 8:
        try:
            i_fields = [int(x) for x in fields]
        except ValueError:
            print(f"Non-integer value in packet\n")
            return

        if i_fields[0] != 1:
            print(f"Invalid packet type {i_fields[0]}\n")
            return

        device = dev_table.get_device(i_fields[1])

        if device is None:
            # device needs to be initialized
            device = esp.EspStatus(i_fields[1])
            dev_table.add_device(device)

            print(f"Found new device (id={i_fields[1]}) at {address}\n")

        else:
            print(f"Status received from device {i_fields[1]}\n")

        device.address = address
        device.power_good = bool(i_fields[2])
        device.mode = esp.EspMode(i_fields[3])
        device.shoulder_status = esp.DynamixelStatus(i_fields[4])
        device.elbow_status = esp.DynamixelStatus(i_fields[5])
        device.odometer = i_fields[6]
        device.points_left = i_fields[7]

        dev_table.device_updated(i_fields[1])

    else:
        print("Invalid packet received: {} fields\n".format(len(fields)))


class ReceiveWrapper(QObject):
    def __init__(self, parent: QObject, socket: QTcpSocket, device_table: esp.DeviceTable):
        super().__init__(parent)
        self.socket = socket
        self.data = bytearray()
        self.parent = parent
        self.esp_table = device_table

        self.socket.readyRead.connect(self.handle_incoming_data)
        self.socket.disconnected.connect(self.handle_socket_disconn)

        if self.socket.bytesAvailable() > 0:
            self.handle_incoming_data()

    @pyqtSlot()
    def handle_incoming_data(self):
        new_data = self.socket.readAll()
        self.data.extend(new_data.data())

        print(f"Read {len(new_data)} from {self.socket.peerAddress().toString()}")

    @pyqtSlot()
    def handle_socket_disconn(self):
        print(f"Connection from {self.socket.peerAddress().toString()} closed")
        handle_packet(self.data, self.socket.peerAddress().toString(), self.esp_table)
        self.parent.handle_close_connection(self)


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
    pkt[WFIELD_N_PTS] = n_pts

    for i in range(0, n_pts):
        p_type, x, y = pt_list[i]
        pt_offset = WFIELD_POINTS + (i * WPOINT_LEN)

        pkt[pt_offset] = p_type.value
        write_packet_xy(pkt, pt_offset + WPOINT_X_OFFSET, x)
        write_packet_xy(pkt, pt_offset + WPOINT_Y_OFFSET, y)

    return pkt


def send_points(parent: QObject, address, points: List[Tuple[PathElementType, float, float]]):
    data = create_points_pkt(points)
    xmitter = TransmitWrapper(parent)
    xmitter.start_transmit(address, data)


def create_mode_change_pkt(new_mode: esp.EspMode) -> bytes:
    pkt = bytearray(WPKT_SETTING_LEN)
    apply_header(pkt, WPacketType.WPKT_SETTING)
    pkt[WFIELD_SETTING_ID] = EspSetting.MODE.value
    pkt[WFIELD_SETTING_VAL] = new_mode.value

    return pkt


def send_mode_change(parent: QObject, address, new_mode: esp.EspMode):
    data = create_mode_change_pkt(new_mode)
    xmitter = TransmitWrapper(parent)
    xmitter.start_transmit(address, data)
