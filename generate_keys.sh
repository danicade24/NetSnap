#!/bin/bash

mkdir keys

ssh-keygen -t rsa -b 4096 -f keys/netsnap_id_rsa -N ""

cp keys/netsnap_id_rsa.pub pc-ssh

cp keys/netsnap_id_rsa backend