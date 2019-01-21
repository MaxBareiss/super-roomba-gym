# super-roomba-gym
# Copyright (C) 2019 Max Bareiss

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
import time
from math import sqrt, pi, sin, cos
import cairo
import numpy as np
import shapely
import shapely.geometry


def euc(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def rotate(a, th):
    return (cos(th) * a[0] - sin(th) * a[1], sin(th) * a[0] + cos(th) * a[1])


class Room:
    def __init__(self, max_size=(3, 3)):
        self.corners = list()
        self.obstacles = list()
        self.max_size = max_size
        self.reward_surface = cairo.ImageSurface(cairo.FORMAT_A8, 1000, 1000)
        self.reward_ctx = cairo.Context(self.reward_surface)
        # self.generate()

    def add_sub_room(self, start, end):
        # print(self.corners)
        start_pt = self.corners[start]
        end_pt = self.corners[end]
        max_width = euc(start_pt, end_pt)
        par = ((end_pt[0] - start_pt[0]) / max_width, (end_pt[1] - start_pt[1]) / max_width)
        perp = rotate(par, -pi / 2)
        width = random.uniform(0.18, max_width / 2.0)
        location = random.uniform(0.0, max_width - width)
        depth = random.uniform(0.18, width)
        p1 = (start_pt[0] + par[0] * location, start_pt[1] + par[1] * location)
        self.corners.insert(start + 1, p1)
        p2 = (p1[0] + perp[0] * depth, p1[1] + perp[1] * depth)
        self.corners.insert(start + 2, p2)
        p3 = (p2[0] + par[0] * width, p2[1] + par[1] * width)
        self.corners.insert(start + 3, p3)
        p4 = (p3[0] - perp[0] * depth, p3[1] - perp[1] * depth)
        self.corners.insert(start + 4, p4)

    def generate_space(self):
        space_size = (random.uniform(2.0, self.max_size[0]), random.uniform(2.0, self.max_size[1]))
        last_corner = self.corners[-1]
        self.corners.append((last_corner[0] + space_size[0], last_corner[1]))
        last_corner = self.corners[-1]
        self.corners.append((last_corner[0], last_corner[1] + space_size[1]))
        last_corner = self.corners[-1]
        self.corners.append((last_corner[0] - space_size[0], last_corner[1]))
        i = 0
        while True:
            if random.uniform(0, 1) < 0.4:
                self.add_sub_room(i, (i + 1) % len(self.corners))
                i += 4
            i += 1
            if i > len(self.corners) - 1:
                break

    def generate_walls(self):
        self.corners = list()
        self.corners.append((0.0, 0.0))
        self.generate_space()

    def generate_chair(self, loc, theta, size, radius):
        pts = [(0, 0), (size, 0), (size, size), (0, size)]
        for pt in pts:
            rot = rotate(pt, theta)
            res = (rot[0] + loc[0], rot[1] + loc[1])
            self.obstacles.append((res, radius))

    def generate_obstacles(self):
        self.obstacles = list()
        # generate_chair((1.3,1.3),0.1,0.4,0.03)

    def generate_reward(self):
        minx = 0
        miny = 0
        maxx = 0
        maxy = 0
        for corner in self.corners:
            if corner[0] < minx:
                minx = corner[0]
            if corner[0] > maxx:
                maxx = corner[0]
            if corner[1] < miny:
                miny = corner[1]
            if corner[1] > maxy:
                maxy = corner[1]
        scale_x = 1000 / (maxx - minx)
        scale_y = 1000 / (maxy - miny)

        print(minx, miny)
        print(maxx, maxy)

        self.reward_ctx.identity_matrix()

        self.reward_ctx.set_source_rgba(0, 0, 0, 0)
        self.reward_ctx.rectangle(0, 0, 1000, 1000)
        self.reward_ctx.fill()

        self.reward_ctx.scale(scale_x, scale_y)
        self.reward_ctx.translate(-minx, -miny)

        self.scale_x = scale_x
        self.scale_y = scale_y
        self.minx = minx
        self.miny = miny

        # self.reward_ctx.set_source_rgba(1, 1, 1, 1)
        # self.reward_ctx.set_line_width(0.03)
        # self.reward_ctx.move_to(self.corners[0][0], self.corners[0][1])
        # for pt in self.corners[1:]:
        #    self.reward_ctx.line_to(pt[0], pt[1])
        # self.reward_ctx.line_to(self.corners[0][0], self.corners[0][1])
        # self.reward_ctx.stroke()
        # self.reward_surface.write_to_png("reward.png")

    def get_reward(self, loc, r):
        self.reward_ctx.set_source_rgba(1, 1, 1, 1)
        self.reward_ctx.arc(loc[0], loc[1], r, 0, 2 * pi)
        self.reward_ctx.fill()

        map = np.frombuffer(self.reward_surface.get_data(), dtype=np.uint8)

        scaled_shape = list()
        for corner in self.corners:
            new_corner_x = (corner[0] + self.minx) * self.scale_x
            new_corner_y = (corner[1] + self.miny) * self.scale_y
            new_corner = (new_corner_x, new_corner_y)
            #print(new_corner)
            scaled_shape.append(new_corner)

        # print("HERE!")

        scaled_shape = shapely.geometry.Polygon(scaled_shape)

        room_area = scaled_shape.area

        return np.sum(map) / room_area / 255

    def generate(self, seed=None):
        if seed is None:
            random.seed(time.time())
        else:
            random.seed(seed)
        self.generate_walls()
        self.generate_obstacles()
        self.generate_reward()

    def render(self, ctx: cairo.Context):
        ctx.save()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(0.03)
        ctx.move_to(self.corners[0][0], self.corners[0][1])
        for pt in self.corners[1:]:
            ctx.line_to(pt[0], pt[1])
        ctx.line_to(self.corners[0][0], self.corners[0][1])
        ctx.stroke()
        ctx.restore()
