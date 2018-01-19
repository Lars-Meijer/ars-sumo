#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from constants import *

import os
import sys
import optparse

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


def run():
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        began = False
        if VEH_ID in traci.vehicle.getIDList():
            began = True
            traci.vehicle.setSpeedMode(VEH_ID, 0)
            traci.vehicle.setSpeed(VEH_ID, 30)
            lane = traci.vehicle.getLaneID(VEH_ID);
            print(traci.lane.getMaxSpeed(lane));
            print(traci.vehicle.getSpeed(VEH_ID))
            print(traci.vehicle.getDistance(VEH_ID))
            print(traci.vehicle.getLeader(VEH_ID))
        elif began:
            print("Collision detected")


    # traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/%s.sumocfg" % PREFIX,
                             "--tripinfo-output", "tripinfo.xml"])
    run()
