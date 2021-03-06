#! /usr/bin/python

import rospy as rp
import geomtwo.msg as gms

import threading as thd

import numpy as np

import circumnavigation_moving_target.srv as dns
import geometry_msgs.msg as gm

LOCK = thd.Lock()
#Initial position
position = np.array(rp.get_param('initial_position'))
#Velocity
velocity = None

stop=False
stop_publish=False

delay=rp.get_param('delay')
rp.sleep(delay)
rp.init_node('integrator')

FREQUENCY = 15e1
RATE = rp.Rate(FREQUENCY)
TIME_STEP = 1.0/FREQUENCY


# Handler for the service "RemoveSensor"
def remove_vehicle_handler(req):   
    global stop_publish
    LOCK.acquire()
    stop_publish=True
    LOCK.release()
    return dns.RemoveAgentResponse()

rp.Service('RemoveVehicle', dns.RemoveAgent, remove_vehicle_handler)


#Publisher
pub = rp.Publisher('position', gms.Point, queue_size=10)
#Publisher position+time
y_pub= rp.Publisher(name='y', data_class=gm.PointStamped, queue_size=10)


#Subscriber
def cmdvel_callback(msg):
    global velocity
    LOCK.acquire()
    velocity = np.array([msg.x, msg.y])
    LOCK.release()
rp.Subscriber(
    name='cmdvel',
    data_class=gms.Vector,
    callback=cmdvel_callback,
    queue_size=10)


start = False
while not rp.is_shutdown() and not start:
    LOCK.acquire()
    if not velocity is None:
        start = True
    #Position message
    y_msg=gm.PointStamped()
    y_msg.header.seq=0
    y_msg.header.stamp = rp.Time.now()
    y_msg.point.x=position[0]
    y_msg.point.y=position[1]
    y_msg.point.z=0
    LOCK.release()
    #Initial position publishing
    pub.publish(gms.Point(x=position[0], y=position[1]))
    y_pub.publish(y_msg)
    RATE.sleep()
while not rp.is_shutdown():
    LOCK.acquire()
    if stop_publish:
        rp.signal_shutdown("agent vehicle removed")
    #Integration
    position = position+velocity*TIME_STEP
    #Position+time message
    y_msg=gm.PointStamped()
    y_msg.header.seq=0
    y_msg.header.stamp = rp.Time.now()
    y_msg.point.x=position[0]
    y_msg.point.y=position[1]
    y_msg.point.z=0
    LOCK.release()
    #Position publishing
    pub.publish(gms.Point(x=position[0], y=position[1]))
    y_pub.publish(y_msg)
    RATE.sleep()
