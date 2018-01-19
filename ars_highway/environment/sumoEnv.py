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
        self.maxSpeed = 40
        self.minSpeed = 0
        self.minDeltaVelocity = -30
        self.minDecelLead = -5

        self.minDistance = -1
        self.maxDistance = 500
        self.maxDeltaVelocity = 30
        self.maxDecelLead = 5

        high = np.array([
            self.maxSpeed,
            self.maxDistance,
            self.maxDeltaVelocity,
            self.maxDecelLead
        ])
        low = np.array([
            self.minSpeed,
            self.minDistance,
            self.minDeltaVelocity,
            self.minDecelLead
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

        self.config_path = "../data/{}.sumocfg".format(PREFIX)

    def _step(self, action):
        traci_data = traci.vehicle.getSubscriptionResults()

        # 2 percent chance to randomly change the speed of the lead car
        if np.random.rand() <= 0.02:
            rand = np.random.rand() * 3
            if rand <= 1:
                traci.vehicle.setType("car1", "slow_car")
            elif rand <= 2:
                traci.vehicle.setType("car1", "car")
            else:
                traci.vehicle.setType("car1", "fast_car")

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
            velocity = traci_data[VEH_ID][VAR_SPEED]
            distance = traci_data[VEH_ID][VAR_LEADER][1]
            deltaVelocity = traci_data["car1"][VAR_SPEED]
            decel = traci_data["car1"][VAR_APPARENT_DECEL]
            reward = self.getReward(velocity, distance)

            self.state = (velocity, distance, deltaVelocity, decel)

            if self.log:
                print("%.2f %d %.2f" % (traci_data[VEH_ID][VAR_SPEED], action, reward))
            if self.test:
                self.run.append(distance)
            return np.array(self.state), reward, False, {}
        return np.array(self.state), -10000, True, {}

    def getReward(self, speed, distance):
        reward = 0
        factor = 10/self.getSpeedReward(MAX_LANE_SPEED)
        reward += factor*self.getSpeedReward(speed)
        reward += self.getDistanceReward(speed, distance)
        return reward

    # Give a low reward for low speeds, high reward for driving the maximum speed
    # and a negative reward for going too fast
    def getSpeedReward(self, speed):
        return -1 * (1 / (MAX_LANE_SPEED / (6 / 7))) * speed ** 7 + speed ** 6

    # A negative reward for driving too close to the car in front
    def getDistanceReward(self, distance, speed):
        if distance <= 0:
            return 0
        else:
            return -1*(speed/distance)

    def _reset(self):
        if self.test and len(self.run) != 0:
            self.result.append(list(self.run))
            self.run.clear()

        traci.load(["-c", self.config_path])
        traci.simulationStep(21 * 100)

        # Setup environment
        speed = rn.randint(15, 25)
        traci.vehicle.setSpeedMode(VEH_ID, 0)
        traci.vehicle.setSpeed(VEH_ID, speed)

        traci.simulationStep()

        # subscribe the vehicles to get their data.
        traci.vehicle.subscribe(VEH_ID, [VAR_SPEED])
        traci.vehicle.subscribe("car1", [VAR_SPEED, VAR_APPARENT_DECEL])
        traci.vehicle.subscribeLeader(VEH_ID, 500)
        self.state = (speed, 1000, 0, 0)
        return np.array(self.state)

    def start(self, gui=False):
        sumoBinary = checkBinary('sumo-gui') if gui else checkBinary('sumo')
        traci.start([sumoBinary, "-n", "../data/{}.net.xml".format(PREFIX)])
        self.traci_data = traci.vehicle.getSubscriptionResults()

    def close(self):
        traci.close()