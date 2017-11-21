from __future__ import absolute_import
from __future__ import print_function

import logging


import constants
import gym
import numpy as np
from gym import spaces
from gym.utils import seeding
from constants import *

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

logger = logging.getLogger(__name__)
log = False

class SumoEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 50
    }

    def __init__(self):
        self._seed()

        # Speeds in meter per second
        self.maxSpeed = 20
        self.minSpeed = 0

        # distances
        self.minDistance = 0
        self.maxDistance = 500

        high = np.array([
            self.maxSpeed,
            self.maxDistance
        ])
        low = np.array([
            self.minSpeed,
            self.minDistance
        ])

        # Observation space of the environment
        self.observation_space = spaces.Box(low, high)
        self.action_space = spaces.Discrete(2)

        self._seed()
        self.viewer = None
        self.state = None

        self.started = False

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def _step(self, action):
        # apply the given action
        if action == 0:
            traci.vehicle.setSpeed(VEH_ID, traci.vehicle.getSpeed(VEH_ID) + 1)
        if action == 1:
            traci.vehicle.setSpeed(VEH_ID, traci.vehicle.getSpeed(VEH_ID) - 1)

        # Run a step of the simulation
        traci.simulationStep()

        # Check the result of this step and assign a reward
        if VEH_ID in traci.vehicle.getIDList():

            lane = traci.vehicle.getLaneID(VEH_ID)
            if traci.vehicle.getSpeed(VEH_ID) > traci.lane.getMaxSpeed(lane):
                reward = -10
            else:
                reward = (traci.vehicle.getSpeed(VEH_ID)/(traci.lane.getMaxSpeed(lane)) - traci.simulation.getCurrentTime()/10000)

            self.state = (traci.vehicle.getSpeed(VEH_ID), traci.vehicle.getDistance(VEH_ID))

            if traci.simulation.getCurrentTime() % 100 == 0 and log:
                print("%.2f %d %.2f" % (traci.vehicle.getSpeed(VEH_ID), action, reward))
            return np.array(self.state), reward, False, {}
        return np.array(self.state), 0, True, {}

    def _reset(self):
        sumoBinary = checkBinary('sumo-gui')

        # close the simulation running before
        # todo see if this can be changed
        if self.started:
            traci.close()

        # Start the next simulation
        traci.start([sumoBinary, "-c", "data/highway.sumocfg"])
        traci.simulationStep()
        traci.vehicle.setSpeed(VEH_ID, 0)
        self.started = True

        self.state = self.np_random.uniform(low=0, high=20, size=(2,))

        return np.array(self.state)
