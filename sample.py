from timeit import main

import netmiko
import napalm
import time
import sys
import re
import argparse



from netmiko import ConnectHandler
from napalm import get_network_driver


def dev_connect(vendor,ip,username, password):

    '''
    Connect to any vednor device
    Vendor agnosting with the proper device handles'

    Note: This mainly takes care of the netmiko module
    :return:
    '''
    driver = get_network_driver(vendor)
    global device_handle
    device_handle= driver(ip, username, password)
    if device_handle.open() == None:
        print("*** Succeesfully Connected to the Device ***")

    def get_info():

        '''
        After getting the handle of the device get the device info
        :return:
        '''
    facts = device_handle.get_facts()
    time.sleep(3)
    #print the contents
    for k,v in facts.items():
        print k,v
    #get the interface status
    int_stat = device_handle.get_interfaces()
    time.sleep(3)
    for i,j in int_stat.items():
        print i,j
    #get arp table for the device
    ##arp_table = device_handle.get_arp_table()
    #time.sleep(3)
    #for i in arp_table():
    #    print i

def configure_configs(toreplace_path):

    '''
    1. Use NAPALM to replace the running config with a new config
    2. Once the config is pushed compare the config with the existing device config
    3. Prompts the user to commit or discard the configs
    :return:
    '''

    #load the config .txt file into the box.
    #NOTE: This doesnt commit the configs

    print toreplace_path

    device_handle.load_replace_candidate(filename = toreplace_path)
    time.sleep(4)
    if device_handle.load_replace_candidate() == None:
        print("*** The configs are loaded but not yet committed")
    #compare the config
    diffs = device_handle.compare_config()
    match = re.search(r'[a-b].*', str(diffs))
    if match.group() is not None:
        print ("*** There are config differences ***")
        #print the differences
        print device_handle.compare_config()
    else:
        print("*** There are no Config Differences ***")

    #Based on user_opt value decide whether to commit or discard

def commit_or_discard(user_opt):

    if user_opt == 'y':
        #Go ahead with the commit
        device_handle.commit_config()
        if device_handle.commit_config is None:
            time.sleep(3)
            print('*** Config is Committed to the Running Config in the Box ***')
        else:
            print('*** There is a problem check ***')
    elif user_opt == 'n':
        #User Didnt want to commit.Proceed with Discard
        device_handle.discard_config()
        if device_handle.discard_config is None:
            time.sleep(3)
            print('*** Configs are discarded as per the user request ***')


def merge_cfg(merge_path):

    '''
    Provide a new config to me merged with a existing config
    The new config will merge along with the existing device config
    :param merge_path:
    :return:
    '''

    device_handle.load_merge_candidate(filename= merge_path)
    if device_handle.load_merge_candidate is None:
        print("*** Configs are loaded.Need user permission to commit or discard ***")
        time.sleep(2)
        device_handle.compare_config()
        if device_handle.compare_config is not None:
            print(" Ask User whether to commit or discard")
            merge_opt = raw_input("Enter 'y' if u want to commit:")
            if merge_opt == 'y':
                print("Commiting the config")
                commit_or_discard(merge_opt)
            else:
                print("Discarding the config")
                commit_or_discard('n')
        else:
            raise Exception
    else:
        raise Exception


if __name__ == "__main__":

    vendor_rtr = raw_input("Enter the Vendor Name:")
    dev_ip = raw_input("Enter the device IP:")
    usr_name = raw_input("Enter the device Username:")
    dev_pass = raw_input("Enter the device Password:")
    dev_connect(vendor_rtr, dev_ip, usr_name, dev_pass)
    load_new_cfg = raw_input("Enter the dev cfg location :")
    configure_configs(load_new_cfg)
    option = raw_input("Do you want to Commit or Discard.IF 'Y' commit or if 'n' then discard")
    commit_or_discard(option)
    cfg_tomerge = raw_input("Merge Config location:")
    merge_cfg(cfg_tomerge)


















