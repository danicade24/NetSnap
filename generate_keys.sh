#!/bin/bash

mkdir keys

ssh-keygen -t rsa -b 4096 -f keys/netsnap_id_rsa -N "netsnap"