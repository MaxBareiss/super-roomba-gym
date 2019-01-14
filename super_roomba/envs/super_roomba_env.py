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


class SuperRoombaEnv(gym.Env):
    def __init__(self):
        self.__version__ = "0.0.1"
        self.room = Room()
        self.seed = None

    def step(self, action):
        pass

    def reset(self):
        self.room.generate(seed=self.seed)

    def seed(self, seed=None):
        if seed is not None:
            self.seed = None
