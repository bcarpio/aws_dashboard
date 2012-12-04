#!/usr/bin/python
# vim: set expandtab:
import os
def get_ec2_conf():
    AWS_ACCESS_KEY_ID = 'YOUR ACCESS KEY ID'
    AWS_SECRET_ACCESS_KEY = 'YOUR SECRET ACCESS KEY'
    return {'AWS_ACCESS_KEY_ID' : AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY' : AWS_SECRET_ACCESS_KEY}

def region_list():
    region_list = ['us-east-1','us-west-1','us-west-2']
    return region_list
