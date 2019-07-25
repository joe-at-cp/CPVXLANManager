#!/usr/bin/python

# VXLAN creation and management tool for autoscaling Check Point gateways
# Joe Dillig - Check Point Software 2019 - dilligj@checkpoint.com
# 07242019

import argparse, subprocess, json

version='07242019'
vxlan_config_file="vxlan.json"

#Input Examples
# vxlan.py -add -dev eth0 -src 10.200.1.10 -dst 4.2.3.1 -id 200 -dstport 7586 -net 192.168.145.1/24 
# vxlan.py -delete -id 200
# vxlan.py -load -config /home/admin/vxlan.json
# vxlan.py -show

parser = argparse.ArgumentParser(prog='VXLAN creation and management tool '+version, usage='./vxlan.py -add [-dev <IF Name> -src <Tunnel Source IP> -dst <Local Private IP of Tunnel> -id <VXLAN Tunnel ID> -net <Tunnel inside subnet> | -del   -sync')

#Arguments
parser.add_argument('-add', help='Adds a new VXLAN tunnel interface',action='store_true', required=False)
parser.add_argument('-dev', help='Interface name (eg eth0)')
parser.add_argument('-src', help='Tunnel Source Ip (typically local ip or elastic ip)', required=False)
parser.add_argument('-dst', help='Destination IP (Ip of remote tunnel endpoint)', required=False)
parser.add_argument('-dstport', help='Destination port to use for tunnel', required=False)
parser.add_argument('-id', help='Numerical identifier for vxlan tunnel interface (used to add or delete vxlan interfaces)', required=False)
parser.add_argument('-net', help='Subnet inside vxlan tunnel (eg 192.168.1.1/24)', required=False)
parser.add_argument('-delete', help='Removed a specified VXLAN tunnel based on ID parameter (-id)', action='store_true', required=False)
parser.add_argument('-sync', help='Syncronizes VXLAN tunnels across all gateways in the autoscaling group', required=False)
parser.add_argument('-show', help='Shows current VXLAN configuration', action='store_true', required=False)
parser.add_argument('-load', help='Loads VXLAN configuration from vxlan.json file', action='store_true', required=False)
parser.add_argument('-config', help='VXLAN configuration file', required=False)
parser.add_argument('-v', '--version', help='Displays script version', action='store_true', required=False)

#Parse and Store Args
args = parser.parse_args()
add = args.add
add_dev = args.dev
add_src = args.src
add_dst = args.dst
add_dstport = args.dstport
add_id = args.id
add_net = args.net
delete = args.delete
delete_id = args.id
sync = args.sync
show = args.show
load = args.load


#Add VXLAN Interface
def add(add_dev,add_src,add_dst,add_dstport,add_id,add_net):

    try:
        subprocess.Popen('ip link add vxlan'+str(add_id)+' type vxlan id '+str(add_id)+' dev '+str(add_dev)+' remote '+str(add_dst)+' local '+str(add_src)+' dstport '+str(add_dstport), shell=True)
        subprocess.Popen('ip addr add '+str(add_net)+' dev vxlan'+str(add_id), shell=True)
        subprocess.Popen('ip link set vxlan'+str(add_id)+' up', shell=True)
        print("Created VXLAN Interface: vxlan"+str(add_id))

    except Exception as e:
        print('Well crap, it broke...')
        raise


#Delete VXLAN Interface
def delete(delete_id):

    try:
        subprocess.Popen('ip link del dev vxlan'+str(delete_id), shell=True)
        print("Removed VXLAN interface: vxlan"+str(delete_id))

        #Remove from vxlan.json file below
        obj  = json.load(open(vxlan_config_file))

        # Iterate through the objects in the JSON and pop (remove)                      
        # the obj once we find it.                                                      
        for i in xrange(len(obj)):
            if obj["interfaces"][i]["name"] == "vxlan"+str(delete_id):
                obj.pop(i)
                break

        # Output the updated file with pretty JSON                                      
        open("updated-file.json", "w").write(
            json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')))


    except Exception as e:
        print('Well crap, it broke...')
        raise


#Sync VXLAN Interfaces on all autoscaled gateways
def sync():
    print("This doesn't really do anything yet... soz bud")

#Version
if args.version == True:
    print("Check Point VXLAN Management Tool")
    print("Joe Dillig - Check Point Software Technologies - dilligj@checkpoint.com")
    print("Version "+version)

#Sync Interfaces
if args.sync == True:
    sync()

#Add New Interface
if args.add == True:
    #Does the vxlan interface already exist?
    add(add_dev,add_src,add_dst,add_dstport,add_id,add_net)
    #Summary of created interface

#Delete Interface
if args.delete == True:
    delete(delete_id)


#Show Configuration
if args.show == True:
    with open(vxlan_config_file) as f:
        vxlan_config = json.load(f)
        print json.dumps(vxlan_config, indent=4, sort_keys=True)


#Load Configuration
if args.load == True:
    print("Loading VXLAN configuration from "+str(vxlan_config_file))
    vxlan_config_file=args.config

    with open(vxlan_config_file) as f:
        vxlanconfig = json.load(f)
    
    for interface in vxlanconfig["interfaces"]:
        add(interface["dev"],interface["local"],interface["remote"],interface["dstport"],interface["id"],interface["net"])
       

