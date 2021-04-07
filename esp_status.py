import enum
from typing import Dict, List, Optional

from PyQt5.QtCore import pyqtSignal, QAbstractTableModel, Qt, QVariant, QModelIndex


class EspSetting(enum.IntEnum):
    MODE = 1
    SPEED = 2


class EspMode(enum.IntEnum):
    IDLE = 0
    DRAW = 1
    PAUSE = 2


class EspDrawSpeed(enum.IntEnum):
    DSPEED_MAX = 0
    DSPEED_25 = 1
    DSPEED_50 = 2
    DSPEED_75 = 3
    DSPEED_100 = 4


class DynamixelStatus(enum.IntEnum):
    STATUS_OK = 0
    RESULT_FAIL = 1
    INSTRUCT_ERR = 2
    CRC_MISMATCH = 3
    DATA_RANGE_ERR = 4
    DATA_LEN_ERR = 5
    DATA_LIMIT_ERR = 6
    ACCESS_ERR = 7


class EspStatus:
    def __init__(self, dev_id: int):
        self.__dev_id = dev_id
        self.address = None  # type: Optional[str]
        self.power_good = False
        self.mode = EspMode.IDLE
        self.shoulder_status = DynamixelStatus.STATUS_OK
        self.elbow_status = DynamixelStatus.STATUS_OK
        self.odometer = 0
        self.points_left = 0

    @property
    def dev_id(self) -> int:
        return self.__dev_id


device_headers = [
    "ID",
    "Address",
    "Power",
    "Mode",
    "Shoulder",
    "Elbow",
    "Odo",
    "To Go"
]
n_device_col = len(device_headers)

device_columns = [
    lambda d: d.dev_id,
    lambda d: d.address,
    lambda d: d.power_good,
    lambda d: d.mode,
    lambda d: d.shoulder_status,
    lambda d: d.elbow_status,
    lambda d: d.odometer,
    lambda d: d.points_left
]


class DeviceTable(QAbstractTableModel):
    device_modified = pyqtSignal(int)

    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.device_list = []  # type: List[EspStatus]
        self.device_map = {}  # type: Dict[int, EspStatus]

    def __iter__(self):
        for dev in self.device_list:
            yield dev

    @property
    def is_empty(self):
        return len(self.device_list) == 0

    def add_device(self, dev_status: EspStatus):
        self.layoutAboutToBeChanged.emit()

        self.device_map[dev_status.dev_id] = dev_status
        self.device_list = sorted(self.device_map.values(), key=lambda d: d.dev_id)

        self.layoutChanged.emit()
        self.device_modified.emit(dev_status.dev_id)

    def get_device(self, dev_id: int) -> Optional[EspStatus]:
        if dev_id in self.device_map:
            return self.device_map[dev_id]
        else:
            return None

    def device_updated(self, dev_id: int):
        for idx, dev in enumerate(self.device_list):
            if dev_id == dev.dev_id:
                self.dataChanged.emit(self.index(idx, 0), self.index(idx, n_device_col - 1))
                self.device_modified.emit(dev_id)
                return

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if (orientation == Qt.Vertical) and (role == Qt.DisplayRole):
            return device_headers[section]

        return None

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 8

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.device_list)

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return QVariant.Invalid

        if role == Qt.DisplayRole:
            device = self.device_list[index.column()]
            return device_columns[index.row()](device)

        else:
            return None

