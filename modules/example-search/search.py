"""
	An image search interface.
"""
import urlparse, urllib
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pyelasticsearch import ElasticSearch

def format_es_result(result):
	logger.info(result)
	return dict(title=result.get('h1', ''),
				desc=result.get('summary_text',''),
				url=result.get('link_url', ''))


class Search():
	"""
		This class will be instantiated by the server to respond to search queries. You shouldn't
		make any assumptions about how many instances will be created, or their lifetime.
	"""
	
	
	def search(self,query, count, offset, **kwargs):
		"""
			Takes a query and performs a search. This returns the list of results as a Python array
			of objects with the standard document field definitions.
		"""
		es = ElasticSearch('http://localhost:9200/')
		dsl ={ 'query' : {'bool' : {'must' : { 'match' : { '_all' : query }}}}}
		results_raw = es.search( dsl, index='example', doc_type='pages', size=count)
		results = [format_es_result(r['_source']) for r in results_raw['hits']['hits']]
		return results
