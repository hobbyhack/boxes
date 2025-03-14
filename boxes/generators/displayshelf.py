#!/usr/bin/env python3
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

class DisplayShelf(Boxes): # change class name here and below
    """Shelf with slanted floors"""

    ui_group = "Shelf"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        self.buildArgParser(x=400, y=100, h=300, outside=True)
        self.argparser.add_argument(
            "--num",  action="store", type=int, default=3,
            help="number of shelves")
        self.argparser.add_argument(
            "--front_wall_height",  action="store", type=float, default=20.0,
            help="height of front walls")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=30.0,
            help="angle of floors (negative values for slanting backwards)")
        self.argparser.add_argument(
            "--include_back", action="store", type=boolarg, default=False,
            help="Include panel on the back of the shelf")
        self.argparser.add_argument(
            "--slope_top", action="store", type=boolarg, default=False,
            help="Slope the sides and the top by front wall height")

    def generate_finger_holes(self):
        t = self.thickness
        a = self.radians
        hs = (self.sl+t) * math.sin(a) + math.cos(a) * t
        for i in range(self.num):
            pos_x = abs(0.5*t*math.sin(a))
            pos_y = hs - math.cos(a)*0.5*t + i * (self.h-abs(hs)) / (self.num - 0.5)
            if a < 0:
                pos_y += -math.sin(a) * self.sl
            self.fingerHolesAt(pos_x, pos_y, self.sl, -self.angle)
            pos_x += math.cos(-a) * (self.sl+0.5*t) + math.sin(a)*0.5*t
            pos_y += math.sin(-a) * (self.sl+0.5*t) + math.cos(a)*0.5*t
            self.fingerHolesAt(pos_x, pos_y, self.front_wall_height, 90-self.angle)

    def generate_sloped_sides(self, width, height):
        top_segment_height = height/self.num
        a = self.radians

        #Maximum size to cut out
        vertical_cut = top_segment_height - self.front_wall_height
        hypotenuse = vertical_cut / math.sin(a)
        horizontal_cut = math.sqrt((hypotenuse ** 2) - (vertical_cut ** 2))

        if (horizontal_cut > width):
            #Shrink the cut to keep the full height
            horizontal_cut = width - 1 #keep a 1mm edge on the top
            vertical_cut =  horizontal_cut * math.tan(a)
            hypotenuse = math.sqrt((horizontal_cut ** 2) + (vertical_cut ** 2))

        top = width - horizontal_cut
        front = height - vertical_cut

        borders = [width, 90, front, 90-self.angle, hypotenuse, self.angle, top, 90, height, 90]
        edges = 'eeeef' if self.include_back else 'e'
        self.polygonWall(borders, edge=edges, callback=[self.generate_finger_holes], move="up", label="left side")
        self.polygonWall(borders, edge=edges, callback=[self.generate_finger_holes], move="up", label="right side")

    def generate_rectangular_sides(self, width, height):
        edges = "eeee"
        if self.include_back:
            edges = "eeef"
        self.rectangularWall(width, height, edges, callback=[self.generate_finger_holes], move="up", label="left side")
        self.rectangularWall(width, height, edges, callback=[self.generate_finger_holes], move="up", label="right side")

    def generate_shelves(self):
        if self.front_wall_height:
            for i in range(self.num):
                self.rectangularWall(self.x, self.sl, "ffef", move="up", label=f"shelf {i+1}")
                self.rectangularWall(self.x, self.front_wall_height, "Ffef", move="up", label=f"front lip {i+1}")
        else:
            for i in range(self.num):
                self.rectangularWall(self.x, self.sl, "Efef", move="up", label=f"shelf {i+1}")

    def render(self):
        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        front = self.front_wall_height
        thickness = self.thickness

        if self.outside:
            x = self.adjustSize(x)
            if self.include_back:
                y = self.adjustSize(y)

        self.radians = a = math.radians(self.angle)
        self.sl = (y - (thickness * (math.cos(a) + abs(math.sin(a)))) - max(0, math.sin(a) * front)) / math.cos(a)

        # render your parts here
        if self.slope_top:
            self.generate_sloped_sides(y, h)
        else:
            self.generate_rectangular_sides(y, h)

        self.generate_shelves()

        if self.include_back:
            self.rectangularWall(x, h, "eFeF", label="back wall", move="up")

