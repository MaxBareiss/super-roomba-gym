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

from super_roomba.envs.room import Room, euc, rotate
import shapely
import shapely.geometry
import shapely.ops
from math import sin, cos, pi, sqrt
import cairo
import numpy as np


class DistanceSensor:
    pt = (0, 0)
    theta = 0
    min_dist = 0
    max_dist = 1000
    sense_dist = None

    def __init__(self, pt, theta, min_dist, max_dist):
        self.pt = pt
        self.theta = theta
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.sense_dist = -1

    def raycast(self, loc, theta, room):
        #print("**********")
        pt1x = self.pt[0] + cos(self.theta) * self.min_dist
        pt1y = self.pt[1] + sin(self.theta) * self.min_dist
        pt2x = self.pt[0] + cos(self.theta) * self.max_dist
        pt2y = self.pt[0] + sin(self.theta) * self.max_dist

        pt1 = (pt1x, pt1y)
        pt2 = (pt2x, pt2y)

        pt1 = rotate(pt1, theta)
        pt1 = (pt1[0] + loc[0], pt1[1] + loc[1])

        pt2 = rotate(pt2, theta)
        pt2 = (pt2[0] + loc[0], pt2[1] + loc[1])

        line = shapely.geometry.LineString([pt1, pt2])

        outline = shapely.geometry.LinearRing(room.corners)

        contact_pts = outline.intersection(line)

        if isinstance(contact_pts, shapely.geometry.Point):

            center = rotate(self.pt, theta)
            center = (center[0] + loc[0], center[1] + loc[1])

            pt = (contact_pts.x, contact_pts.y)
            dist = euc(pt, center)

            #print("DIST")
            #print(pt)
            #print(center)

            #print(dist)

            if self.min_dist < dist < self.max_dist:
                self.sense_dist = dist
            else:
                self.sense_dist = -1
        elif isinstance(contact_pts, shapely.geometry.GeometryCollection):
            if len(contact_pts) == 0:
                self.sense_dist = -1

        #print(contact_pts)
        #print(self.sense_dist)

    def render(self, ctx: cairo.Context):
        pt1x = self.pt[0] + cos(self.theta) * self.min_dist
        pt1y = self.pt[1] + sin(self.theta) * self.min_dist
        pt2x = self.pt[0] + cos(self.theta) * self.max_dist
        pt2y = self.pt[0] + sin(self.theta) * self.max_dist

        ctx.set_line_width(0.0125)

        if self.sense_dist < 0:
            ctx.set_source_rgb(1, 0.5, 0.5)
        else:
            ctx.set_source_rgb(0.5, 1.0, 0.5)

        ctx.move_to(pt1x, pt1y)
        ctx.line_to(pt2x, pt2y)
        ctx.stroke()

        if self.sense_dist >= 0:
            sensex = self.pt[0] + cos(self.theta) * self.sense_dist
            sensey = self.pt[1] + sin(self.theta) * self.sense_dist

            ctx.arc(sensex, sensey, 0.025, 0, 2 * pi)
            ctx.stroke()


class Roomba:
    def __init__(self):
        self.loc = None
        self.theta = None
        self.wheel_vel = None
        self.sensors = list()
        self.r = 0.17
        self.sensors = [DistanceSensor((0, 0), 40 / 180 * pi, 0.17, 0.3),
                        DistanceSensor((0, 0), -40 / 180 * pi, 0.17, 0.3)]
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
            # print("NEAREST DIST: ", nearest_dist)
            if nearest_dist < self.r:
                delta = shapely.geometry.Point((nearest_pt[0].x - center.x, nearest_pt[0].y - center.y))
                delta_len = euc((0, 0), (delta.x, delta.y))
                delta = shapely.geometry.Point(delta.x / delta_len, delta.y / delta_len)
                new_x = center.x - delta.x * (self.r - nearest_dist + 0.0001)
                new_y = center.y - delta.y * (self.r - nearest_dist + 0.0001)
                # print("NEW X: ", new_x)
                self.loc = (new_x, new_y)
            else:
                break
            # print(self.loc)

    def observe(self, room: Room):
        obs = list()
        for sensor in self.sensors:
            sensor.raycast(self.loc, self.theta, room)
            obs.append(sensor.sense_dist)
        obs = np.array(obs)
        return obs

    def step(self, wheel_acc, room: Room, dt):
        left_wheel_vel = max(-0.4, min(0.4, self.wheel_vel[0] + wheel_acc[0] * dt))  # 400 mm/s
        right_wheel_vel = max(-0.4, min(0.4, self.wheel_vel[1] + wheel_acc[1] * dt))  # 400 mm/s
        self.wheel_vel = (left_wheel_vel, right_wheel_vel)

        self.move(dt)
        self.apply_physics(room)
        return self.observe(room)

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

        for sensor in self.sensors:
            sensor.render(ctx)

        ctx.restore()
