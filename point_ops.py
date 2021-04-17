from abc import ABC, abstractmethod
from enum import IntEnum
from typing import List


ARM_REACH = 40.0

class PathElementType(IntEnum):
    NONE = 0
    MOVE = 1
    PEN_UP = 2
    PEN_DOWN = 3
    END = 4


class ESPPoint:
    def __init__(self, path_type: PathElementType = PathElementType.NONE, x: float = 0, y: float = 0):
        self.pt_type = path_type
        self.x = x
        self.y = y

    def scale(self, s) -> 'ESPPoint':
        return ESPPoint(self.pt_type, self.x * s, self.y * s)

    def offset(self, x, y):
        return ESPPoint(self.pt_type, self.x + x, self.y + y)


class AbstractPointIterator(ABC):
    def __init__(self, field_width: float, field_height: float):
        self.field_width = field_width
        self.field_height = field_height
        self.pt_scale = 1
        self.x_offset = 0.0
        self.y_offset = 0.0

    @property
    def is_empty(self):
        return not self.has_next_point()

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def has_next_point(self) -> bool:
        pass

    @abstractmethod
    def dequeue_next_point(self) -> ESPPoint:
        pass

    def set_scale(self, len_cm: float):
        self.pt_scale = len_cm / self.field_width

    def set_offset(self, x_cm: float, y_cm: float):
        self.x_offset = x_cm
        self.y_offset = y_cm

    def get_points(self, max_count: int) -> List[ESPPoint]:
        count = 0
        pt_list = []

        while (count < max_count) and self.has_next_point():
            next_point = self.dequeue_next_point()

            next_point = ESPPoint(next_point.pt_type, next_point.x, self.field_height - next_point.y)
            next_point = next_point.offset(-(self.field_width / 2), 0)\
                .scale(self.pt_scale)\
                .offset(self.x_offset, self.y_offset)

            pt_list.append(next_point)
            count += 1

        return pt_list
