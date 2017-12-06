from __future__ import absolute_import
from __future__ import print_function

import logging

import constants
import gym
import numpy as np
from gym import spaces
from constants import *
import random as rn

import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
from traci.constants import *

# Setting the seeds to get reproducible results
os.environ['PYTHONHASHSEED'] = '0'
np.random.seed(42)
rn.seed(12345)

gui = False
sumoBinary = checkBinary('sumo-gui') if gui else checkBinary('sumo')
config_path = "../data/{}.sumocfg".format(PREFIX)


# noinspection PyMethodMayBeStatic
class SumoEnv(gym.Env):

    def __init__(self):
        # Speeds in meter per second
        self.maxSpeed = 20
        self.minSpeed = 0

        high = np.array([
            self.maxSpeed
        ])
        low = np.array([
            self.minSpeed
        ])

        # Observation space of the environment
        self.observation_space = spaces.Box(low, high)
        self.action_space = spaces.Discrete(3)

        self.viewer = None
        self.state = None
        self.log = False
        self.result = []
        self.run = []
        self.test = False

    def getReward(self, data):
        return (-((4 * (data[VEH_ID][VAR_SPEED] - MAX_LANE_SPEED)) ** 2)) + MAX_LANE_SPEED

    def _step(self, action):
        before_step = traci.vehicle.getSubscriptionResults()
        if VEH_ID in before_step:
            # apply the given action
            if action == 0:
                traci.vehicle.setSpeed(VEH_ID, before_step[VEH_ID][VAR_SPEED] + 0.25)
            if action == 2:
                traci.vehicle.setSpeed(VEH_ID, before_step[VEH_ID][VAR_SPEED] - 0.25)

        # Run a step of the simulation
        traci.simulationStep()

        after_step = traci.vehicle.getSubscriptionResults()
        # Check the result of this step and assign a reward
        if VEH_ID in after_step:
            reward = self.getReward(after_step)

            self.state = after_step[VEH_ID][VAR_SPEED]

            if self.log:
                print("{:.2f} {:d} {:.2f}".format(after_step[VEH_ID][VAR_SPEED], action, reward))
                if self.test:
                    self.run.append(after_step[VEH_ID][VAR_SPEED])
            return np.array(self.state), reward, False, {}
        return np.array(self.state), 0, True, {}

    def _reset(self):
        if self.test and len(self.run) != 0:
            self.result.append(list(self.run))
            self.run.clear()

        traci.load(["-c", config_path])
        traci.simulationStep()

        # Setup environment
        speed = rn.randint(1, 8)
        traci.vehicle.setSpeedMode(VEH_ID, 0)
        traci.vehicle.setSpeed(VEH_ID, speed)

        traci.simulationStep()

        # subscribe the vehicles to get their data.
        traci.vehicle.subscribe(VEH_ID, [VAR_SPEED])

        self.state = speed
        return np.array(self.state)

    def close(self):
        traci.close()


traci.start([sumoBinary, "-c", config_path])
