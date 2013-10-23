"""
	An example which makes use of the search-interface component. This launches a host
	which has the search interface and provides a test search interface.
"""
from fabric.api import task, local, run, cd

import cliqz
import cliqz_tasks as std
import search_tasks as sc

from entity_extractor import ee
from db_install import db

import search_interface
from elastic_search import esc

# You need to change this name for your app, and likely to run this test
app_name = 'sample-search-oct15'

@task 
def config_dev_host():
	"""config host for development"""
	cliqz.cli.prep_dev_host()
	search_interface.config_dev_host()

@task 
def install_esc():
	"""Installs an ElasticSearch node on the host. This is meant for a local virtual machine for testing."""
	esc.install(
		cluster_name = app_name,
		heap_size = 1,
		single_node = True, # You only want this for testing, remove for any >1 node size cluster
	)

@task
def install_entity_extractor():
	db.install_db()
	ee.install_ee()

@task
def build_entity_db():
	cliqz.cli.ensure_dir('/mnt/data/')
	with cd('/mnt/data/'):
		run('wget http://source-packages.clyqz.com/de_loc.txt')
	run('python /opt/entity-extractor/create_db.py /mnt/data/de_loc.txt /mnt/data/de_loc')


@task
def full_install(host_details = None):
	install_entity_extractor()
	cliqz.cli.python_package('pyelasticsearch')
	pkg = cliqz.package.gen_definition()
	local( "tar cjf {} modules indexing data".format( pkg['local'] ) )
	cliqz.package.install( pkg, '/opt/' + app_name )
	
	search_interface.install( 
		module_path = '/opt/' + app_name + '/modules',
		class_name = 'sample-search.search.Search',
		results_template = 'combined'
	)

cliqz.setup(
	app_name = app_name,
	zabbix = {
		'base': 'linux-64'
	},
	search = {
		'primary_install': full_install,
		# This is an arbitrary name for the ElasticSearch cluster (default for sc.* tasks)
		'default_cluster': 'bell',
	},
)
