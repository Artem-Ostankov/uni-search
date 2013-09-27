from pyelasticsearch import ElasticSearch
import json as simplejson
import urlparse
import codecs
import simplejson as json


es = ElasticSearch('http://localhost:9200/')
data = open('../data/data_part0.jl', 'r' )
for l in data:
	new_l = l.rstrip()
	json_object = json.loads(new_l)
	print json_object
	#es.index('example', 'pages', json_object)

