import math
from typing import List, Tuple

import cv2

from point_ops import AbstractPointIterator, ESPPoint, PathElementType


def distance(p2, p1):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


class ContourIterator(AbstractPointIterator):
    def __init__(self, contours, width_px, height_px):
        super().__init__(width_px, height_px)

        # moves contains the next contour to move to from the current index
        self.contours = contours
        self.contour_idx = 0
        self.point_in_contour = 0
        self.moves = []
        self.sent_end = False
        self.cm_per_px = 1.0

        averages = [cv2.mean(contour) for contour in contours]

        # initially, all are unvisited except the start point
        unvisited_idx = list(range(1, len(averages)))
        current_idx = 0

        while len(unvisited_idx) > 0:
            cur_point = averages[current_idx]

            # find the next point that is closest to the current
            min_dist = float('inf')
            min_idx = -1

            for dest_idx in unvisited_idx:
                tgt_distance = distance(averages[dest_idx], cur_point)

                if tgt_distance < min_dist:
                    min_idx = dest_idx
                    min_dist = tgt_distance

            current_idx = min_idx
            unvisited_idx.remove(min_idx)
            self.moves.append(min_idx)

    def reset(self):
        self.contour_idx = 0
        self.point_in_contour = 0
        self.sent_end = False

    @property
    def current_contour(self):
        return self.contours[self.contour_idx]

    def __has_next_contour(self) -> bool:
        # if there is a next move defined for current contour
        return self.contour_idx < len(self.moves)

    def __move_next_contour(self):
        self.contour_idx = self.moves[self.contour_idx]
        self.point_in_contour = 0

    def has_next_point(self) -> bool:
        return (self.point_in_contour < len(self.current_contour)) or self.__has_next_contour() or not self.sent_end

    def dequeue_next_point(self) -> ESPPoint:
        if self.point_in_contour < len(self.current_contour):
            # normal point
            # each contour is an array of single-element point arrays
            point = self.current_contour[self.point_in_contour][0]
            elem_type = PathElementType.MOVE if (self.point_in_contour > 0) else PathElementType.PEN_DOWN

            self.point_in_contour += 1

            return ESPPoint(elem_type, point[0], point[1])

        elif self.__has_next_contour():
            # break to next contour
            point = self.current_contour[-1][0]
            self.__move_next_contour()
            return ESPPoint(PathElementType.PEN_UP, point[0], point[1])

        else:
            # nothing left to process
            if not self.sent_end:
                self.sent_end = True
                return ESPPoint(PathElementType.END, 0, 0)
            else:
                return ESPPoint(PathElementType.NONE, 0, 0)


