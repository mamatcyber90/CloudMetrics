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

# Split results into seperate files

raw_results = open("results.txt", "r")
trimmed_results = open("lines.txt",'w')

start_strings = list()
end_strings = list()

for line in raw_results:
    if (line[:2] == 'WR'):
        trimmed_results.write(line)
    elif (line[13:18] == "start"):
        start_strings.append(line[24:].strip()) # only picks the relevant bits
    elif (line[13:16] == "end"):
        end_strings.append(line[24:].strip())

raw_results.close()
trimmed_results.close()

# Read results into Python
gflops = pandas.read_csv("lines.txt", header=None, delim_whitespace=True).get(6).values.round(3)

# get python date objects from start/end times
start_objs = [datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y") for date in start_strings]
end_objs = [datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y") for date in end_strings]

# Convert Python date objects into ISO 8601 format
# If duration < 1 second (i.e. startdate == enddate) make end date 1 second after startdate

start_iso_list = [obj.isoformat() for obj in start_objs]
end_iso_list = list()

iso_fmt = ""
for i in range(len(start_objs)):
    # if time is the same, artificially add one second to end
    # otherwise, use the given timestamp
    if ((end_objs[i] - start_objs[i]) == datetime.timedelta(0)):
        end_objs[i] = start_objs[i] + datetime.timedelta(0,1)

    iso_fmt = end_objs[i].isoformat()
    end_iso_list.append(iso_fmt)

### Build JSON Body ###

# convert string into a python object
samples = list(zip(start_iso_list,end_iso_list,gflops))

body = {"batch_started":start_iso_list[0],
        "test_type": test_type,
        "instance_type": instance_type,
        "cloud_provider": cloud,
        "cloud_region": region,
        "os": "centos7",
        "samples":samples}

prettybody = json.dumps(body, indent=4)
signature = base64.b64encode(hmac.new(secret_key.encode(), prettybody.encode(), digestmod=hashlib.sha256).digest()).decode()


print("The Signature is: {}".format(signature))

# Post to recieving server

headers = {"X-UG-Signature":signature,
           "Accept":"application/json",
           "Content-Type":"application/json"}

responce = requests.post(ingress_url,data=prettybody, headers=headers)
print(responce.status_code)

print(prettybody)
