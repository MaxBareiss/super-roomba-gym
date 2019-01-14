import gym
from gym import spaces
import numpy as np
from .room import Room

class SuperRoombaEnv(gym.Env):
    def __init__(self):
        self.__version__ = "0.0.1"

    def step(self, action):
        pass

    def reset(self):
        pass

    def seed(self, seed=None):
        pass