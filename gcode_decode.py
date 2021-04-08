import math
from typing import List, Tuple

import numpy as np

from point_ops import AbstractPointIterator, ESPPoint, PathElementType


class GCodeIterator(AbstractPointIterator):
    def __init__(self, commands: List[ESPPoint], width_cm):
        super().__init__(width_cm)

        self.commands = commands
        self.command_idx = 0
        self.sent_end = False

    def reset(self):
        self.command_idx = 0
        self.sent_end = False

    def has_next_point(self) -> bool:
        return (self.command_idx < len(self.commands)) or not self.sent_end

    def dequeue_next_point(self):
        if self.command_idx < len(self.commands):
            cur_point = self.commands[self.command_idx]
            self.command_idx += 1
            return cur_point

        elif not self.sent_end:
            return ESPPoint(PathElementType.END, 0, 0)

        else:
            return ESPPoint(PathElementType.NONE, 0, 0)


def load_gcode_commands(filename: str) -> [List[ESPPoint], float, float]:
    """ Try to load commands from the given file. Returns (commands, max_x, max_y) """

    gcode = open(filename, "r")

    commands = []  # type: List[ESPPoint]
    last_move_point = ESPPoint()

    max_x = 0.0
    max_y = 0.0

    for file_line in gcode:
        line = file_line.rstrip().upper()

        if line.startswith('G1'):
            parts = line.split(' ')

            if parts[1].startswith('Z'):
                # pen up/down
                z_level = float(parts[1][1:])
                cmd_type = PathElementType.PEN_DOWN if (z_level == 0) else PathElementType.PEN_UP

                commands.append(ESPPoint(cmd_type, last_move_point.x, last_move_point.y))

            elif parts[1].startswith('X'):
                # movement
                x = float(parts[1][1:])
                max_x = max(max_x, x)

                y = float(parts[2][1:])
                max_y = max(max_y, y)

                last_move_point = ESPPoint(PathElementType.MOVE, x, y)
                commands.append(last_move_point)

    return commands, max_x, max_y


def get_contours_from_path(path: List[ESPPoint], max_x, max_y):
    scale = 1000 / max(max_x, max_y)
    width = math.ceil(max_x * scale)
    height = math.ceil(max_y * scale)

    contours = []
    current_contour = []

    for point in path:
        if point.pt_type == PathElementType.PEN_UP:
            # end of contour
            if len(current_contour) > 0:
                contours.append(np.array(current_contour))
                current_contour = []

        elif point.pt_type == PathElementType.MOVE:
            current_contour.append([[round(point.x * scale), round(point.y * scale)]])

    return contours, width, height
