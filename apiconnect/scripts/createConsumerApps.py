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
    if not server:
        server = raw_input("Server:")
    if not org:
        org = raw_input("Org:")
    if not catalog:
        catalog = raw_input("Catalog:")
    if not user:
        user = raw_input("Portal Username:")
    if not password:
        password = getpass.getpass("Portal Password:(will be hidden)")
    if not file:
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
    try:
        consumerOrgId=json.loads(response.content)[0]['id']
    except:
        prRed("Error al obtener el token de acceso. Por favor, verifique las credenciales introducidas")
        exit(0)
        
    with open(file) as info_file:
        for line in info_file:
            orginApp=line.split()
            prYellow('Name: ' +orginApp[0])
            newApp={
               "name": orginApp[0],
               "credentials":
               {
                  "clientID": "true",
                  "clientSecret": "true"
               }
               ,
               "public": "true"
               }

#createAPP
            response = session.post('https://'+server+'/v1/portal/orgs/'+consumerOrgId+'/apps',data=json.dumps(newApp), auth= (user,password),headers=headers,verify= False)
            prLightGray("Created consumer App: "+response.content)
            consumerAppId=json.loads(response.content)['id']

#changeClientId
#            consumerAppClientSecret=base64.b64encode(hashlib.sha256(orginApp[2]).digest())
#            credentials={
#               "clientID": orginApp[1],
#               "clientSecret": consumerAppClientSecret,
#               "description": "none"
#            }

#         response=session.put('https://'+server+'/v1/portal/orgs/'+consumerOrgId+'/apps/'+consumerAppId+'/credentials',data=json.dumps(credentials), auth= (user,password), headers=headers, verify= False)
#          prRed("Changed credentials for: "+response.content)



if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])
    exit(0)
