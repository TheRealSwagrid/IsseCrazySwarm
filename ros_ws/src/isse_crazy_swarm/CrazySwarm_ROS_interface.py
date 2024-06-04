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
from visualization_msgs.msg import Marker
from tf import TransformListener


class CrazySwarm_ROS_interface:

    def __init__(self):
        self.copter = BasicSingleCopter(f"fly@{int(os.environ['semantix_port'])}") #{int(rospy.get_param('~semantix_port'))}")
        self.scale = 0.1
        self.rotation = [0., 0., 0., 1.]
        self.transformListener = TransformListener()
        self.name = f"CrazyFly#{int(rospy.get_param('~semantix_port'))}"
        self.pub = rospy.Publisher("/robot", Marker, queue_size=1)
        self.br = tf.TransformBroadcaster()

    def set_rotation(self, quaternion: list):
        self.rotation = quaternion

    def get_rotation(self):
        return self.rotation

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def rotate(self, axis, deg):
        axis = np.array(axis)
        theta = np.deg2rad(deg)
        self.rotation = list(quaternion_about_axis(theta, axis))
        return self.rotation

    def fly_to(self, p: list):
        # self.cf.setLEDColor(1., 1., 0.)
        self.copter.set_target(np.array(p))

        timer = time.time()
        rospy.logerr(f"Flying to {p}")
        pos = self.get_position()
        dist = math.sqrt((p[0] - pos[0]) ** 2 + (p[1] - pos[1]) ** 2 + (p[2] - pos[2]) ** 2)
        while dist > 0.1:
            pos = self.get_position()
            dist = math.sqrt((p[0] - pos[0]) ** 2 + (p[1] - pos[1]) ** 2 + (p[2] - pos[2]) ** 2)
            time.sleep(.01)
        rospy.logerr(f"Arrived at {p} after {time.time() - timer} seconds")
        # self.cf.setLEDColor(0., 1., 0.)

    def arm(self):
        self.copter.start()

    def disarm(self):
        self.copter.stop()

    def get_position(self):
        pos = self.copter.get_position()
        if pos is None:
            return [0., 0., 0.]
            raise ValueError("Copter isn't available")
        else:
            pos = list(pos)
        return pos

    def get_arming_status(self):
        return self.copter.get_available()

    def publish_visual(self):
        # rospy.logwarn(f"Publishing {self.position}")
        marker = Marker()
        marker.id = int(rospy.get_param('~semantix_port'))
        marker.header.frame_id = "world"
        marker.header.stamp = rospy.Time.now()
        marker.ns = f"crazyfly"
        marker.lifetime = rospy.Duration(0)
        # marker.color.r = .1
        # marker.color.g = .15
        # marker.color.b = .3
        self.position = self.get_position()
        marker.mesh_use_embedded_materials = True
        marker.pose.position.x = self.position[0]
        marker.pose.position.y = self.position[1]
        marker.pose.position.z = self.position[2]
        marker.pose.orientation.x = self.rotation[0]
        marker.pose.orientation.y = self.rotation[1]
        marker.pose.orientation.z = self.rotation[2]
        marker.pose.orientation.w = self.rotation[3]
        # Scale down
        marker.scale.x = self.scale
        marker.scale.y = self.scale
        marker.scale.z = self.scale
        marker.color.a = 1
        marker.type = Marker.MESH_RESOURCE
        marker.action = Marker.ADD
        marker.mesh_resource = r"package://isse_crazy/meshes/copter.dae"

        self.pub.publish(marker)

        # TF
        self.br.sendTransform(self.position,
                              self.rotation, rospy.Time.now(), self.name, "world")


if __name__ == '__main__':
    drone = CrazySwarm_ROS_interface()
    rate = rospy.Rate(30)
    rospy.logwarn("Starting CrazyFly ROS")
    rospy.logwarn("Starting server")

    server = VirtualCapabilityServer(int(rospy.get_param('~semantix_port')), socket.gethostbyname(socket.gethostname()))

    rospy.logwarn("starting isse_copter semanticplugandplay")
    copter = IsseCrazySwarm(server)

    copter.start()
    # signal.signal(signal.SIGTERM, handler)

    drone.publish_visual()
    while not rospy.is_shutdown():
        drone.publish_visual()
        drone.br.sendTransform(drone.position,
                               np.array(drone.rotation), rospy.Time.now(), drone.name, "world")

        rate.sleep()
        # rospy.logwarn(f"Server status: {server.running}, {copter}")
