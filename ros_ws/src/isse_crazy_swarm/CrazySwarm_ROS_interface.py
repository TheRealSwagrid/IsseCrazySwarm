#!/usr/bin/env python3
import math
import os
import socket
import time

# Ros imports
import rospy
import numpy as np
import tf


# isse swarm imports
from isse_basic_swarms.BasicSingleCopter import BasicSingleCopter

# semantic imports
from AbstractVirtualCapability import VirtualCapabilityServer
from tf.transformations import quaternion_about_axis

from IsseCrazySwarm import IsseCrazySwarm


class CrazySwarm_ROS_interface:

    def __init__(self):
        pass

if __name__ == '__main__':
    rospy.init_node('rosnode')#, xmlrpc_port=int(os.environ["xmlrpc_port"]), tcpros_port=int(os.environ["tcpros_port"]))

    semantic_swarm = CrazySwarm_ROS_interface()
    rate = rospy.Rate(30)

    server = VirtualCapabilityServer(int(rospy.get_param('~semantix_port')), socket.gethostbyname(socket.gethostname()))

    swarm = IsseCrazySwarm(server)

    swarm.start()
    # signal.signal(signal.SIGTERM, handler)

    while not rospy.is_shutdown():
        rate.sleep()

