#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
author: thomas.atchley
"""

import pandas
import sys
import os
import json
import time
import subprocess
import platform
import multiprocessing as mp
import datetime
import hashlib
import requests
import base64
import hmac

# Look for parameters
test_type = sys.argv[1]
cloud = sys.argv[2]
instance_type = sys.argv[3]
region = sys.argv[4]
secret_key = sys.argv[5]
ingress_url = sys.argv[6]
os = sys.argv[7]

# Split results into seperate files
for line in raw_results:
    if (line.find('(groupid=') != -1):
        print("hi")
        start_strings.append(" ".join(line.split()[7:])) # gets start time
    elif (line.find('mixed') == 2):
        iops.append(line.split()[3][5:]) # add iops value
        end_strings.append(int(line.split()[-1][:-4])) # add the miliseconds to end strings for now


raw_results.close()
trimmed_results.close()

# Read results into Python

# get python date objects from start/end times
start_objs = [datetime.datetime.strptime(date, "%b %d %H:%M:%S %Y") for date in start_strings]
end_objs = list()
for i in range(len(start_objs)):
        end_objs.append(start_objs[i]+datetime.timedelta(milliseconds=end_strings[i]))

# Convert Python date objects into ISO 8601 format

start_iso_list = [obj.isoformat() for obj in start_objs]
end_iso_list = [obj.isoformat()[:-7] for obj in end_objs] # removes miliseconds

### Build JSON Body ###

# convert string into a python object
samples = list(zip(start_iso_list,end_iso_list,gflops))

body = {"batch_started":start_iso_list[0],
        "test_type": test_type,
        "instance_type": instance_type,
        "cloud_provider": cloud,
        "cloud_region": region,
        "os": os,
        "samples":samples}

prettybody = json.dumps(body, indent=4)
signature = base64.b64encode(hmac.new(secret_key.encode(), prettybody.encode(), digestmod=hashlib.sha256).digest()).decode()


print("The Signature is: {}".format(signature))

# Post to recieving server

headers = {"X-UG-Signature":signature,
           "Accept":"application/json",
           "Content-Type":"application/json"}

responce = requests.post(ingress_url,data=prettybody, headers=headers)
print("Responce code: {}".format(responce.status_code))

with open("responce.txt", 'w') as f:
    f.write(str(responce.status_code))

print(prettybody)
