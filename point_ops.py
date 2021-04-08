from abc import ABC, abstractmethod
from enum import IntEnum
from typing import List


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


class AbstractPointIterator(ABC):
    def __init__(self, field_width: float):
        self.field_width = field_width
        self.pt_scale = 1

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

    def get_points(self, max_count: int) -> List[ESPPoint]:
        count = 0
        pt_list = []

        while (count < max_count) and self.has_next_point():
            next_point = self.dequeue_next_point().scale(self.pt_scale)
            pt_list.append(next_point)
            count += 1

        return pt_list
