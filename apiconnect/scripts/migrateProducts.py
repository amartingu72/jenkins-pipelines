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
import re
import subprocess
import getpass
import sys, getopt
import os
import datetime
import yaml
import requests
import json

import urllib3

import base64
import hashlib


def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))


def signal_handler(sig, frame):
        print('Keyboard signal detected. Stopping.')
        sys.exit(0)

def main(argv):

    OrigFolder=""
    DestinationServer = ""
    DestinationOrg = ""
    DestinationCatalog = ""
    DestinationUser = ""
    DestinationPassword = ""

    try:
      opts, args = getopt.getopt(argv,"h:s:o:c:u:p:f:", ["server=", "org=", "catalog=", "user=", "password=", "folder="])
    except getopt.GetoptError:
      prGreen("master.py -s <server> -o <org> -c <catalog> -u <user> -p <password> -f <folder> ")
      sys.exit(2)
    for opt, arg in opts:
      if opt == "-h":
         prGreen("master.py -s <server> -o <org> -c <catalog> -u <user> -p <password> -f <folder> ")
         sys.exit()
      elif opt in ("-s", "--server"):
         DestinationServer = arg
      elif opt in ("-o", "--org"):
         DestinationOrg = arg
      elif opt in ("-c", "--catalog"):
         DestinationCatalog = arg
      elif opt in ("-u", "--user"):
         DestinationUser = arg
      elif opt in ("-p", "--password"):
         DestinationPassword = arg
      elif opt in ("-f", "--folder"):
         OrigFolder = arg

    while not OrigFolder:
        OrigFolder = raw_input("Origin Folder:")
    while not DestinationServer:
        DestinationServer = raw_input("Destination Server:")
    while not DestinationOrg:
        DestinationOrg = raw_input("Destination Org:")
    while not DestinationCatalog:
        DestinationCatalog = raw_input("Destination Catalog:")
    while not DestinationUser:
        DestinationUser = raw_input("Destination Username:")
    while not DestinationPassword:
        DestinationPassword = getpass.getpass("Destination Password:(will be hidden)")

#Start


    if not os.path.exists(OrigFolder):
         raise ValueError(OrigFolder +" NOT FOUND");
    os.chdir(OrigFolder)

    objects=os.listdir(".")

    contieneProducto=False
    for object in objects:
        if re.search('(product)',object):
            contieneProducto=True

    if not contieneProducto:
        print('El directorio origen no contiene elementos de producto')
        exit(0)


    prLightGray("Logging in... to Destination")
    subprocess.check_output(["apic", "login", "-s", DestinationServer, "-u", DestinationUser, "-p", DestinationPassword], shell=True)

    for object in objects:

        isProduct = re.search('(product)',object)

        if isProduct:
            prLightGray("Publishing product: "+object+" in org: "+DestinationOrg+", catalog: "+DestinationCatalog+"...")
            result = subprocess.check_output(["apic", "products:publish",object ,"-s", DestinationServer, "-o", DestinationOrg, "-c", DestinationCatalog], shell=True)
            prCyan("Result: " +result)

    # for object in objects:
    #     fileName = re.findall("\[([a-z]+.*)\]$",object)
    #     os.rm(fileName)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])
    exit(0)
