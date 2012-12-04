from flask import Flask, flash, abort, redirect, url_for, request, render_template, make_response, json, Response
from fabric.api import *
from fabric.operations import local,put
import os, sys
import config
import boto.ec2.elb
import boto
from boto.ec2 import *
from boto.route53.record import ResourceRecordSets


app = Flask(__name__)

@app.route('/')
def index():

	list = []
	creds = config.get_ec2_conf()

	for region in config.region_list():
		conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
		zones = conn.get_all_zones()	
		instance_count = len(conn.get_all_instance_status())  
		ebs = conn.get_all_volumes()
		ebscount = len(ebs)
		unattached_ebs = 0

		for vol in ebs:
			state = vol.attachment_state()
			if state == None:
				unattached_ebs = unattached_ebs + 1

		elis = conn.get_all_addresses()
		eli_count = len(elis)
		unattached_eli = 0

		for eli in elis:
			instance_id = eli.instance_id
			if not instance_id:
				unattached_eli = unattached_eli + 1

		connelb = boto.ec2.elb.connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
		elb = connelb.get_all_load_balancers()
		elb_count = len(elb)
		list.append({ 'region' : region, 'zones': zones, 'instance_count' : instance_count, 'ebscount' : ebscount, 'unattached_ebs' : unattached_ebs, 'eli_count' : eli_count, 'unattached_eli' : unattached_eli, 'elb_count' : elb_count})
		

	print list
	return render_template('index.html',list=list)

@app.route('/ebs_volumes/<region>/')
def ebs_volumes(region=None):
	creds = config.get_ec2_conf()
	conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
	ebs = conn.get_all_volumes()
	ebs_vol = []	
	for vol in ebs:
		state = vol.attachment_state()
		if state == None:
			ebs_vol.append(vol.id)
	return Response(json.dumps(ebs_vol), mimetype='application/json')
			

@app.route('/elastic_ips/<region>/')
def elastic_ips(region=None):
	creds = config.get_ec2_conf()
	conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
	elis = conn.get_all_addresses()
	un_eli = []
	for eli in elis:
		instance_id = eli.instance_id
		if not instance_id:
			un_eli.append(eli.public_ip)
	return Response(json.dumps(un_eli), mimetype='application/json')
			

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
