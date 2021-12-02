#!/usr/bin/env python

# eu-de.apiconnect.ibmcloud.com

# Dowloand and install PyYAML from https://pyyaml.org/wiki/PyYAML
# apic commands at https://www.ibm.com/support/knowledgecenter/en/SSFS6T/com.ibm.apic.toolkit.doc/rapim_cli_command_summary.html
# login using "apic login --sso" before to launch the script
#
# Disclaimer!! devapps, extensions, consumer organizations and properties was not impemented (customer doesn't have them).
# Local objects (config, services, etc.) are not exported.
# spaces and securegateways are not supported.

import signal
#import re
import subprocess
import getpass
import sys, getopt
import os
#import datetime
import yaml
import requests
import json

import urllib3

import base64
import hashlib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))


def signal_handler(sig, frame):
        prGreen('Keyboard signal detected. Stopping.')
        sys.exit(0)

def main(argv):
    server = ""
    org = ""
    catalog = ""
    user = ""
    password = ""
    file= ""
    try:
      opts, args = getopt.getopt(argv,"h:s:o:c:u:p:f:", ["server=", "org=", "catalog=", "user=", "password=", "file="])
    except getopt.GetoptError:
      prGreen("master.py -s <server> -o <organization> -c <catalog> -u <user> -p <password> -f <file> ")
      sys.exit(2)
    for opt, arg in opts:
      if opt == "-h":
         prGreen("master.py -s <server> -o <organization> -c <catalog> -u <user> -p <password> -f <file> ")
         sys.exit()
      elif opt in ("-s", "--server"):
         server = arg
      elif opt in ("-o", "--org"):
         org = arg
      elif opt in ("-c", "--catalog"):
         catalog = arg
      elif opt in ("-u", "--user"):
         user = arg
      elif opt in ("-p", "--password"):
         password = arg
      elif opt in ("-f", "--file"):
         file = arg
    while not server:
        server = raw_input("Server:")
    while not org:
        org = raw_input("Org:")
    while not catalog:
        catalog = raw_input("Catalog:")
    while not user:
        user = raw_input("Portal Username:")
    while not password:
        password = getpass.getpass("Portal Password:(will be hidden)")
    while not file:
        file = raw_input("file:")


    headers = {
    "X-IBM-APIManagement-Context" : org+"."+catalog,
    "Content-Type": "application/json",
     }

    #GetOrgs

    session = requests.Session()
    session.trust_env = False
    response=session.get('https://'+server+'/v1/portal/orgs',auth=(user,password), headers=headers)

    prRed("Orgs: "+response.content)
    consumerOrgId=json.loads(response.content)[0]['id']

    with open(file) as info_file:
        for line in info_file:
            subscription=line.split()
            appName=subscription[0]
            productName=subscription[1]
            productVersion=subscription[2]
            productPlan=subscription[3]

            data={
               "plan": productPlan,
               "product":
               {
                  "name": productName,
                  "version": productVersion
                }
                }

# #createSubscription
            prLightGray("Creating Subscription of app "+appName+" to product "+ productName+ " version "+ productVersion+" and plan "+productPlan)
            response = session.post('https://'+server+'/v1/portal/orgs/'+consumerOrgId+'/apps/'+appName+'/subscriptions',data=json.dumps(data), auth= (user,password),headers=headers,verify= False)
            prLightGray("Subscription: "+response.content)

            


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])
    exit(0)
