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

import gym
from gym import spaces
import numpy as np
from .room import Room
from .roomba import Roomba
import cairo


class SuperRoombaEnv(gym.Env):
    def __init__(self):
        self.__version__ = "0.0.1"
        self.room = Room()
        self.seed = None
        self.bot = Roomba()
        self.dt = 0.1
        self.action_space = spaces.Box(low=np.array([-4, -4], dtype=np.float32),
                                       high=np.array([4, 4], dtype=np.float32))  # m/s^2
        self.observation_space = spaces.Box(low=np.array([-0.4, -0.4, -1, -1], dtype=np.float32),
                                            high=np.array([0.4, 0.4, 0.3, 0.3], dtype=np.float32))
        self.time = 0

    def step(self, action: np.ndarray):
        action[0] = min(4, max(action[0], -4))
        action[1] = min(4, max(action[1], -4))
        obs = self.bot.step(action, self.room, self.dt)

        reward = self.room.get_reward(self.bot.loc, self.bot.r)

        self.time += self.dt

        done = self.time > 600

        return obs, reward, done, {}

    def reset(self):
        self.room.generate(seed=self.seed)
        self.bot.reset()
        self.time = 0

    def seed(self, seed=None):
        if seed is not None:
            self.seed = None

    def render(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000)
        ctx = cairo.Context(surface)
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.rectangle(0, 0, 1000, 1000)
        ctx.fill()
        ctx.scale(1000 / 5, 1000 / 5)
        ctx.translate(1, 1)

        self.room.render(ctx)
        self.bot.render(ctx)

        surface.write_to_png("pics/{:02d}.png".format(int(self.time / self.dt)))
