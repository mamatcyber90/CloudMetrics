#!/bin/bash

az vm create \
    --name $1 \
    --resource-group $2 \
    --image CentOS \
    --admin-username centos \
    --location $3 \
    --authentication-type ssh \
    --size $4 \
    --generate-ssh-keys \
	  --output tsv >> azure_out.tsv

az vm open-port \
    --name $1 \
    --port 22 \
    --resource-group $2 >> port_open.out
