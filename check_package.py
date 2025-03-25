from scholarly import scholarly
from scholarly import ProxyGenerator

# Proxy
pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

# Now search Google Scholar from behind a proxy
search_query = scholarly.search_pubs('Perception of physical stability and center of mass of 3D objects')
scholarly.pprint(next(search_query))