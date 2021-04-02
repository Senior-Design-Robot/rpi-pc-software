import enum


class EspSetting(enum.IntEnum):
    SETTING_MODE = 1
    SETTING_SPEED = 2


class EspMode(enum.IntEnum):
    MODE_IDLE = 0
    MODE_DRAW = 1
    MODE_PAUSE = 2


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
        self.dev_id = dev_id
        self.power_good = False
        self.shoulder_status = DynamixelStatus.STATUS_OK
        self.elbow_status = DynamixelStatus.STATUS_OK
        self.odometer = 0
        self.points_left = 0


esp_dict = dict()
