from pyelasticsearch import ElasticSearch
import json
import re
import requests
import urllib


def get_index_settings():
	settings = {
		'settings' : 
			{ 
				'number_of_shards' : 10, 
				'number_of_replicas' : 0,
				'index' :
				{
					'analysis' : {
						'analyzer' : {
							'completion_analyzer':
								{ 'tokenizer' : 'keyword',
								  'filter' : ['lowercase', 'german_snowball' ]
								}		
							},
						'filter' : {
							'german_snowball': {
								'type' : 'snowball',
								'language' : 'German2'
								}
							}
						}
					}
				},
		'mappings' : 
			{
				'pages' :
				{
					'properties' : {
						'text'  : { 'type' : 'string' ,  'index' : 'analyzed' , 'analyzer' : 'cliqz_intrafind_index'},
						'title' :  { 'type' : 'string' , 'index' : 'analyzed' , 'analyzer' : 'cliqz_intrafind_index'},
						'url' : { 'type' : 'string' , 'index' : 'analyzed' , 'analyzer' : 'cliqz_intrafind_index'},
						'suggestions' : { 'type' : 'completion', 'index_analyzer' : 'completion_analyzer', 'search_analyzer' : 'completion_analyzer'}
					}
				}
			} 
		}
	return settings

class Indexer():

	def __init__(self):
		self.es = ElasticSearch('http://localhost:9200/')
		self.index_name = 'example'
		self.mapping = 'pages'


	def index(self, filepath):
		self.pre_bulk_indexing_settings()
		data = open(filepath, 'r')
		bulk_request = []
		for l in data:
			new_l = l.rstrip()
			json_object = json.loads(new_l)
			entry = {  'url' : json_object['link_url'] }
			entry['title'] = json_object['h1']
			entry['text'] = json_object['summary_text']
			entry['suggestions'] = [] 
			entry['suggestions'].append({'input' : entry['title'], 'weight' : 2 })
			#TODO Enable this with entity extraction results
			#entry['suggestions'].append({'input' :[] })
			#entry['suggestions'][1]['input'].append(' '.join([x.strip() for x in parts[i:len(parts) - 2]]))
			bulk_request.append(entry)
			if (len(bulk_request) > 500) :
				self.es.bulk_index(self.index_name, self.mapping, bulk_request)
				del bulk_request[:]
		self.es.bulk_index(self.index_name, self.mapping, bulk_request)
		self.after_bulk_indexing_settings()

	def pre_bulk_indexing_settings(self):
		settings = {
					"index":{
						"refresh_interval": -1,
						"number_of_replicas": 0
						}
					}
		self.update_settings(settings)

	def after_bulk_indexing_settings(self):
		settings = {
					"index":{
						"refresh_interval": 1,
						"number_of_replicas": get_index_settings()['settings'].get('number_of_replicas', 1)
						}
					}
		self.update_settings(settings)

	def update_settings(self, settings):
		self.es.update_settings(self.index_name, settings)

	def register_index(self):
		self.es.create_index(self.index_name, settings=get_index_settings())

	def drop_index(self):
		self.es.delete_index(self.index_name)