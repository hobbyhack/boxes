# Copyright (C) 2013-2016 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *


class TorsionBox(Boxes):
    """Flat panel with two skins sandwiching an interlocking rib grid"""

    ui_group = "Box"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.buildArgParser(x=200, y=150, h=30)
        self.argparser.add_argument(
            "--nx", action="store", type=int, default=4,
            help="number of cells along x")
        self.argparser.add_argument(
            "--ny", action="store", type=int, default=3,
            help="number of cells along y")
        self.argparser.add_argument(
            "--skins", action="store", type=boolarg, default=True,
            help="also render the two outer skins")

    def render(self):
        x, y, h = self.x, self.y, self.h
        nx, ny = self.nx, self.ny

        if nx < 1 or ny < 1:
            raise ValueError("nx and ny must be >= 1")

        sx = [x / nx] * nx
        sy = [y / ny] * ny

        # y-ribs: length y, slots cut from bottom where interior x-ribs cross.
        for i in range(nx + 1):
            bottom = edges.SlottedEdge(self, sy, "e", slots=0.5 * h)
            self.rectangularWall(
                y, h, [bottom, "e", "e", "e"],
                move="up", label=f"y-rib {i + 1}")

        # x-ribs: length x, slots cut from top where interior y-ribs cross.
        # Top edge is traversed right-to-left, so reverse the section list.
        for i in range(ny + 1):
            top = edges.SlottedEdge(self, sx[::-1], "e", slots=0.5 * h)
            self.rectangularWall(
                x, h, ["e", "e", top, "e"],
                move="up", label=f"x-rib {i + 1}")

        if self.skins:
            self.rectangularWall(x, y, "eeee", move="up", label="skin 1")
            self.rectangularWall(x, y, "eeee", move="up", label="skin 2")
