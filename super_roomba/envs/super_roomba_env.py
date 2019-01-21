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


class SuperRoombaEnv(gym.Env):
    def __init__(self):
        self.__version__ = "0.0.1"
        self.room = Room()
        self.seed = None
        self.bot = Roomba()
        self.dt = 0.1
        self.action_space = spaces.Box(low=np.array([-2, -2]), high=np.array([2, 2]))  # m/s^2

    def step(self, action: np.ndarray):
        action[0] = min(4, max(action[0], -4))
        action[1] = min(4, max(action[1], -4))
        self.bot.step(action, self.room, self.dt)

    def reset(self):
        self.room.generate(seed=self.seed)
        self.bot.reset()

    def seed(self, seed=None):
        if seed is not None:
            self.seed = None
