from gym.envs.registration import register

register(
    id="SuperRoomba-v0",
    entry_point='super_roomba.envs:SuperRoombaEnv'
)