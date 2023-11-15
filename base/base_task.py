import pandas as pd
from itertools import product
from abc import abstractmethod


class BaseTask(object):
    def __init__(self, config):
        self.config = config
        self.cfg_query = self.config['query']
        self.queries = self.setup_queries(self.cfg_query)
        
    def setup_queries(self, cfg_query):
        prefixs = cfg_query['prefixs']
        postfixs = cfg_query['postfixs']
        main = cfg_query['main']
        queries = {
            idx: "".join(values) 
            for idx, values in enumerate(list(product(prefixs, main, postfixs)))
        }
        return queries
    
    @abstractmethod
    def run(self, *inputs):        
        return