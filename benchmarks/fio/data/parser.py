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

test_type = sys.argv[1]
cloud = sys.argv[2]
instance_type = sys.argv[3]
region = sys.argv[4]
secret_key = sys.argv[5]
ingress_url = sys.argv[6]
os = sys.argv[7]
interval = sys.argv[8]
jobfile = sys.argv[9]


start_times = list()
end_times = list()
iops = list()
latency = list()

with open("fio.json") as fulltext:
    tests=fulltext.read().replace("}\n{","}\n*\n{").split("*")

    for i in range(len(tests)):
        fiojson = json.loads(tests[i])

        start_times.append(datetime.datetime.fromtimestamp(int(fiojson['timestamp'])))
        end_times.append(start_times[i]+datetime.timedelta(seconds=int(interval)))
        iops.append(fiojson['jobs'][0]['mixed']['iops'])
        latency.append(fiojson['jobs'][0]['mixed']['lat']['mean'])

start_iso = [date.isoformat() for date in start_times]
end_iso = [date.isoformat() for date in end_times]

iops_samples = list(zip(start_iso,end_iso,iops))
latency_samples = list(zip(start_iso,end_iso,latency))


def sendResult(filename,samples, starttime, test_type):

    global ingress_url
    global instance_type
    global cloud
    global region
    global os

    body = {"batch_started":starttime,
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

    with open(filename, 'w') as f:
        f.write(str(responce.status_code))

    print(prettybody)


####


sendResult("iops_responce.txt",iops_samples, start_iso[0], "{}-{}".format(test_type,jobfile))
sendResult("lat_responce.txt",latency_samples, start_iso[0], "{}-{}-latency".format(test_type,jobfile))
