"""
	An example which makes use of the search-interface component. This launches a host
	which has the search interface and provides a test search interface.
"""

# The deploy_modules needs to be in the PYTHONPATH for the "search_interface" module
import sys, os
#sys.path.append( 'extern/search-interface/deploy_modules' )
#sys.path.append( 'extern/elastic-search-cluster/deploy_modules' )

from fabric.api import task, local

import cliqz
import cliqz_tasks as std
import search_interface
from elastic_search import esc


app_name = 'example-search'

cliqz.setup(
	app_name = app_name,
	zabbix = {
		'base': 'linux-64'
	},
)

@task 
def config_dev_host():
	"""config host for development"""
	cliqz.cli.prep_dev_host()
	search_interface.config_dev_host()


@task 
def install_esc():
	"""Installs an ElasticSearch node on the host"""
	esc.install(
		cluster_name = app_name,
		heap_size = 1,
		single_node = True, # You only want this for testing, remove for any >1 node size cluster
	)


@task
def full_install(host_details = None):
	cliqz.cli.python_package('pyelasticsearch')
	pkg = cliqz.package.gen_definition()
	local( "tar cjf {} modules".format( pkg['local'] ) )
	cliqz.package.install( pkg, '/opt/' + app_name )
	
	search_interface.install( 
		module_path = '/opt/' + app_name + '/modules',
		class_name = 'example-search.search.Search'
	)

@task
def launch(id):
	"""(id) launch a new AWS instance of this project"""
	cliqz.ec2.launch_instance(
		image = 'ubuntu-12.04-64bit',
		security_groups = [ cliqz.ec2.setup_security_group(
			app_name, search_interface.get_security_rules(), add_dmz = True
		)],
		instance_type = 't1.micro',
		install_keys = ['eleni'],
		name = "{}-{}".format( app_name, id ),
		install = full_install
	)

