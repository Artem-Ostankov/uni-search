from pyelasticsearch import ElasticSearch
import json, urlparse
import codecs



es = ElasticSearch('http://localhost:9200/')
data = open('../data/data_part0.jl', 'r' )
for l in data:
	new_l = l.rstrip()
	print new_l
	json_object = json.loads(new_l)
	print json_object
	es.index('example', 'pages',json_object  ,json_object['link_url'])
	exit()

