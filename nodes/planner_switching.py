#! /usr/bin/python

import rospy as rp
import geomtwo.msg as gms
import std_msgs.msg as sms
import threading as thd
import numpy as np
import math
import copy as cp
import circumnavigation_moving_target.srv as dns
import geometry_msgs.msg as gm

# Variables
position = None
estimate = None
# Vector fi of the agent
bearing_measurement = None
# Target position
TARGET_POSITION = rp.get_param('target_position')


# Parameters
DESIRED_DISTANCE = rp.get_param('desired_distance')  # from the .yaml file
alpha= rp.get_param('alpha') # from the .yaml file
k_fi= rp.get_param('k_fi')
k_d= rp.get_param('k_d')

#Influence radius
rho=2*DESIRED_DISTANCE+0.3

node_name=rp.get_param('node_name')
delay=rp.get_param('delay')

# Lock
LOCK = thd.Lock()

stop_publish=False

rp.sleep(delay)
rp.init_node('planner') 

# Counterclockwise_angle function
# This function returns the counterclockwise angle between two vectors knowing the position
def Angle(position,neighbor_position):    
    y_i=np.array([position[0]-TARGET_POSITION[0],position[1]-TARGET_POSITION[1],0.0]) 
    y_j=np.array([neighbor_position[0]-TARGET_POSITION[0],neighbor_position[1]-TARGET_POSITION[1],0.0])
    n_i=np.linalg.norm(y_i)
    n_j=np.linalg.norm(y_j)
    sp=np.inner(y_i,y_j)
    vp=np.cross(y_i,y_j)
    cos_beta=sp/(n_i*n_j)
    sin_beta=vp[2]/(n_i*n_j)
    beta=math.atan2(sin_beta,cos_beta)
    if beta<0:
        beta=beta+2*math.pi
    return beta 


# Subscribers to the positions of the other agents
agent_names=[]
agent_positions = {}
def agent_callback(msg, name):
    global agent_positions
    LOCK.acquire()
    agent_positions[name] = [msg.x, msg.y]
    LOCK.release()


position_subscribers={}
# Handler for the service "AddAgent": the new agent call "AddAgent" and the others add its name in agent_name and subscribe to its fi 
def add_agent_handler(req):
    global agent_names
    global agent_positions
    global position_subscribers
    position_subscribers[req.name]=rp.Subscriber(
        name='/'+req.name+'/position',
        data_class=gms.Point,
        callback=agent_callback,
        callback_args=req.name,
        queue_size=1)   
    LOCK.acquire()
    agent_names.append(req.name)
    agent_positions[req.name]=None
    LOCK.release()
    return dns.AddAgentResponse()

rp.Service('AddAgent', dns.AddAgent, add_agent_handler)

# Handler for the service "RemoveAgent"
def remove_agent_handler(req):   
    global position_subscribers
    global agent_names
    global agent_positions
    LOCK.acquire()
    position_subscribers[req.name].unregister()
    agent_names.remove(req.name)
    del agent_positions[req.name]
    LOCK.release()
    return dns.RemoveAgentResponse()

rp.Service('RemoveAgent', dns.RemoveAgent, remove_agent_handler)

# Call to the service "AddMe": the agent requires to the cloud to add his name
rp.wait_for_service('/AddMe')
add_me_proxy=rp.ServiceProxy('/AddMe', dns.AddAgent)
add_me_proxy.call(node_name)


# Handler for the service "RemovePlanner"
def remove_planner_handler(req):
    global stop_publish   
    LOCK.acquire()
    stop_publish=True
    LOCK.release()
    return dns.RemoveAgentResponse()

rp.Service('RemovePlanner', dns.RemoveAgent, remove_planner_handler)

#Subscribers
def position_callback(msg):
    global position
    LOCK.acquire()
    position = np.array([msg.x, msg.y])
    LOCK.release()
rp.Subscriber(
    name='position',
    data_class=gms.Point,
    callback=position_callback,
    queue_size=1)

def bearing_measurement_callback(msg):
    global bearing_measurement
    LOCK.acquire()
    bearing_measurement = np.array([msg.x, msg.y])
    LOCK.release()
rp.Subscriber(
    name='bearing_measurement',
    data_class=gms.Vector,
    callback=bearing_measurement_callback,
    queue_size=10)

def estimate_callback(msg):
    global estimate
    LOCK.acquire()
    estimate = np.array([msg.x, msg.y])
    LOCK.release()
rp.Subscriber(
    name='estimate',
    data_class=gms.Point,
    callback=estimate_callback,
    queue_size=10)

RATE = rp.Rate(150.0)
start = False

#Publishers
cmdvel_pub = rp.Publisher(
    name='cmdvel',
    data_class=gms.Vector,
    queue_size=10)

beta_pub = rp.Publisher(
    name='beta',
    data_class=gm.PointStamped,
    queue_size=10)

while not rp.is_shutdown() and not start:
    LOCK.acquire()
    if all([not data is None for data in [position, estimate, bearing_measurement]]):
           start = True
    #else:
        #rp.logwarn('waiting for measurements')
    LOCK.release()
    RATE.sleep()
while not rp.is_shutdown():
    LOCK.acquire()
    if stop_publish:
        rp.signal_shutdown("agent planner removed")
    #Bearing vector in the clockwise direction
    phi_bar=np.array([bearing_measurement[1],-bearing_measurement[0]])
    #Number of other agents in the network
    agent_beta=[]
    #Counterclockwise angle
    for name in agent_names:
        if not agent_positions[name] is None and np.linalg.norm(position-agent_positions[name])<=rho:
            agent_beta.append(Angle(position,agent_positions[name]))
                    
    # If there is only one agent beta=2*pi
    beta=0
    if len(agent_beta)>0:
        beta=min(agent_beta)
    #Control law
    est_dist = np.linalg.norm(estimate-position)
    vel = k_d*bearing_measurement*(est_dist-DESIRED_DISTANCE)+k_fi*est_dist*phi_bar*(alpha+beta)
    #Velocity message
    cmdvel_msg = gms.Vector(x=vel[0], y=vel[1])
    #Beta message
    beta_msg=gm.PointStamped()
    beta_msg.header.seq=0
    beta_msg.header.stamp = rp.Time.now()
    beta_msg.point.x=beta
    beta_msg.point.y=0
    beta_msg.point.z=0
    LOCK.release()
    # Publishing
    cmdvel_pub.publish(cmdvel_msg)
    beta_pub.publish(beta_msg)
    RATE.sleep()
