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

# Setting the seeds to get reproducible results
os.environ['PYTHONHASHSEED'] = '0'
np.random.seed(42)
rn.seed(12345)

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

logger = logging.getLogger(__name__)

gui = False
if gui:
    sumoBinary = checkBinary('sumo-gui')
else:
    sumoBinary = checkBinary('sumo')
config_path = "../data/highway.sumocfg"


class SumoEnv(gym.Env):

    def __init__(self):
        # Speeds in meter per second
        self.maxSpeed = 20
        self.minSpeed = 0

        self.minDistance = 0
        self.maxDistance = 500
        high = np.array([
            self.maxSpeed,
            self.maxDistance,
        ])
        low = np.array([
            self.minSpeed,
            self.maxDistance
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

    def _step(self, action):
        traci_data = traci.vehicle.getSubscriptionResults()
        if VEH_ID in traci_data:
            # apply the given action
            if action == 0:
                traci.vehicle.setSpeed(VEH_ID, traci_data[VEH_ID][VAR_SPEED] + 0.25)
            if action == 2:
                traci.vehicle.setSpeed(VEH_ID, traci_data[VEH_ID][VAR_SPEED] - 0.25)
        # Run a step of the simulation
        traci.simulationStep()

        # Check the result of this step and assign a reward
        if VEH_ID in traci_data:
            speed = traci_data[VEH_ID][VAR_SPEED]
            distance = traci_data[VEH_ID][VAR_LEADER][1]
            reward = 0.0000001*(-1*(1 / (MAX_LANE_SPEED / (6 / 7))) * speed ** 7 + speed ** 6)

            self.state = (speed, distance)

            if self.log:
                print("%.2f %d %.2f" % (traci_data[VEH_ID][VAR_SPEED], action, reward))
            if self.test:
                self.run.append(traci_data[VEH_ID][VAR_SPEED])
            return np.array(self.state), reward, False, {}
        return np.array(self.state), -20000, True, {}

    def _reset(self):
        if self.test and len(self.run) != 0:
            self.result.append(list(self.run))
            self.run.clear()

        traci.load(["-c", config_path])
        for _ in range(21):
            traci.simulationStep()

        # Setup environment
        speed = rn.randint(10, 20)
        traci.vehicle.setSpeedMode(VEH_ID, 0)
        traci.vehicle.setSpeed(VEH_ID, speed)

        traci.simulationStep()

        # subscribe the vehicles to get their data.
        traci.vehicle.subscribe(VEH_ID, [VAR_SPEED])
        traci.vehicle.subscribeLeader(VEH_ID, 500)
        self.state = (speed, 1000)
        return np.array(self.state)

    def close(self):
        traci.close()


traci.start([sumoBinary, "-c", config_path])
