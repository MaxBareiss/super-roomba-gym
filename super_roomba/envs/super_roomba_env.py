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
