import enum
from typing import Dict, Optional, Tuple


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


esp_dict = dict()  # type: Dict[int, EspStatus]
