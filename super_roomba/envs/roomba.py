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

from super_roomba.envs.room import Room, euc
import shapely
import shapely.geometry
import shapely.ops
from math import sin, cos, pi
import cairo


class Roomba:
    def __init__(self):
        self.loc = None
        self.theta = None
        self.wheel_vel = None
        self.r = 0.17
        self.reset()

    def reset(self):
        self.loc = (0.001, 0.001)
        self.theta = 0
        self.wheel_vel = (0, 0)

    def move(self, dt):
        # https://chess.eecs.berkeley.edu/eecs149/documentation/differentialDrive.pdf
        if self.wheel_vel[0] == 0 and self.wheel_vel[1] == 0:
            return
        old_x = self.loc[0]
        old_y = self.loc[1]
        half_wb = 0.15  # [m]
        omega = (self.wheel_vel[1] - self.wheel_vel[0]) / half_wb
        if abs(omega) > 1e-6:
            R = half_wb / 2 * (self.wheel_vel[0] + self.wheel_vel[1]) / (self.wheel_vel[1] - self.wheel_vel[0])
            ICC = (old_x - R * sin(self.theta), old_y + R * cos(self.theta))
            new_x = cos(omega * dt) * (old_x - ICC[0]) - sin(omega * dt) * (old_y - ICC[1]) + ICC[0]
            new_y = sin(omega * dt) * (old_x - ICC[0]) + cos(omega * dt) * (old_y - ICC[1]) + ICC[1]
        else:
            new_x = old_x + cos(self.theta) * self.wheel_vel[0] * dt
            new_y = old_y + sin(self.theta) * self.wheel_vel[0] * dt
        self.loc = (new_x, new_y)
        self.theta += omega * dt

    def apply_physics(self, room: Room):
        outline = shapely.geometry.LinearRing(room.corners)
        while True:
            center = shapely.geometry.Point(self.loc)
            nearest_pt = shapely.ops.nearest_points(outline, center)
            nearest_dist = euc((center.x, center.y), (nearest_pt[0].x, nearest_pt[0].y))
            #print("NEAREST DIST: ", nearest_dist)
            if nearest_dist < self.r:
                delta = shapely.geometry.Point((nearest_pt[0].x - center.x, nearest_pt[0].y - center.y))
                delta_len = euc((0,0),(delta.x, delta.y))
                delta = shapely.geometry.Point(delta.x / delta_len, delta.y / delta_len)
                new_x = center.x - delta.x * (self.r - nearest_dist)
                new_y = center.y - delta.y * (self.r - nearest_dist)
                #print("NEW X: ", new_x)
                self.loc = (new_x, new_y)
            else:
                break
            #print(self.loc)

    def step(self, wheel_acc, room: Room, dt):
        left_wheel_vel = max(-0.4, min(0.4, self.wheel_vel[0] + wheel_acc[0] * dt))  # 400 mm/s
        right_wheel_vel = max(-0.4, min(0.4, self.wheel_vel[1] + wheel_acc[1] * dt))  # 400 mm/s
        self.wheel_vel = (left_wheel_vel, right_wheel_vel)

        self.move(dt)
        self.apply_physics(room)

    def render(self, ctx: cairo.Context):
        ctx.save()
        ctx.translate(self.loc[0], self.loc[1])
        ctx.rotate(self.theta)
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.025)
        ctx.arc(0, 0, self.r - 0.0125, 0, 2 * pi)
        ctx.stroke()
        ctx.move_to(self.r - 0.10, 0)
        ctx.line_to(self.r, 0)
        ctx.stroke()
        ctx.restore()
