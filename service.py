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
		instances = conn.get_all_instance_status()
		instance_count = len(instances)
		ebs = conn.get_all_volumes()
		ebscount = len(ebs)
		unattached_ebs = 0
		unattached_eli = 0
		event_count = 0
	
		for instance in instances:
			events = instance.events
			if events:
				event_count = event_count + 1	

		for vol in ebs:
			state = vol.attachment_state()
			if state == None:
				unattached_ebs = unattached_ebs + 1

		elis = conn.get_all_addresses()
		eli_count = len(elis)


		for eli in elis:
			instance_id = eli.instance_id
			if not instance_id:
				unattached_eli = unattached_eli + 1

		connelb = boto.ec2.elb.connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
		elb = connelb.get_all_load_balancers()
		elb_count = len(elb)
		list.append({ 'region' : region, 'zones': zones, 'instance_count' : instance_count, 'ebscount' : ebscount, 'unattached_ebs' : unattached_ebs, 'eli_count' : eli_count, 'unattached_eli' : unattached_eli, 'elb_count' : elb_count, 'event_count' : event_count})
		
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
			ebs_info = { 'id' : vol.id, 'size' : vol.size, 'iops' : vol.iops, 'status' : vol.status }
			ebs_vol.append(ebs_info)
	#return Response(json.dumps(ebs_vol), mimetype='application/json')
	return render_template('ebs_volume.html',ebs_vol=ebs_vol,region=region)
			
@app.route('/ebs_volumes/<region>/delete/<vol_id>')
def delete_ebs_vol(region=None,vol_id=None):
	creds = config.get_ec2_conf()	
	conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
	vol_id = vol_id.encode('ascii')
	vol_ids = conn.get_all_volumes(volume_ids=vol_id)
	for vol in vol_ids:
		result = []
		r = vol.delete()
		result.append(r)
	return Response(json.dumps(result), mimetype='application/json')
	
@app.route('/elastic_ips/<region>/')
def elastic_ips(region=None):
	creds = config.get_ec2_conf()
	conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
	elis = conn.get_all_addresses()
	un_eli = []
	for eli in elis:
		instance_id = eli.instance_id
		if not instance_id:
			eli_info = { 'public_ip' : eli.public_ip, 'domain' : eli.domain}
			un_eli.append(eli_info)
	#return Response(json.dumps(un_eli), mimetype='application/json')
	return render_template('elastic_ip.html',un_eli=un_eli,region=region)

@app.route('/elastic_ips/<region>/delete/<ip>')
def delete_elastic_ip(region=None,ip=None):
	creds = config.get_ec2_conf()
	conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
	ip = ip.encode('ascii')
	elis = conn.get_all_addresses(addresses=ip)

	for eli in elis:
		result = []
		r = eli.release()
		result.append(r)
	return Response(json.dumps(result), mimetype='application/json')

@app.route('/instance_events/<region>/')
def instance_events(region=None):
	creds = config.get_ec2_conf()
	conn = connect_to_region(region, aws_access_key_id=creds['AWS_ACCESS_KEY_ID'], aws_secret_access_key=creds['AWS_SECRET_ACCESS_KEY'])
	instances = conn.get_all_instance_status()
	instance_event_list = []
	for instance in instances:
		event = instance.events
		if event:
			event_info = { 'instance_id' : instance.id, 'event' : instance.event[0].code, 'description' : instance.event[0].description, 'event_before' : instance.event[0].not_before, 'event_after': instance.event[0].not_after }
			instance_event_list.append(event_info)
	return render_template('instance_events.html', instance_event_list=instance_event_list)
			
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
