import time
import random
import pandas as pd
from base import BaseSelenium
from bs4 import BeautifulSoup
from task.tasks import GoogleTask

RANDOM_MIN_SEC = 15
RANDOM_MAX_SEC = 20

class GoogleSelenium(BaseSelenium):
    def __init__(self, config, logger, is_proxy):
        super().__init__(logger, is_proxy)
        self.task = GoogleTask(config)
        self.queries = self.task.queries
        self.logger = logger
        self._domain = "https://www.google.com"
        
    def __call__(self, html) -> pd.DataFrame:
        stacked_df = None
        while True:
            soup = BeautifulSoup(html, 'html.parser')
            if fprs:=soup.find('p', attrs={'id': 'fprs'}):  # 다음 페이지가 존재할 경우
                href = fprs.find('a', attrs={'class': 'spell_orig'})['href']
                html = self.request_query(href, exist_next=True)
                continue
        
            df = self.task.run(soup)
            if stacked_df is None:
                stacked_df = df
            else:
                stacked_df = pd.concat([stacked_df, df], axis=0).reset_index(drop=True)
                
            try:
                pages = soup.find_all('td')[-1]
                if pages.text != '다음': # 다음 페이지가 없을 경우
                    break
                else:
                    href = pages.find('a')['href']
                    html = self.request_query(href, exist_next=True)
            except:
                break
        return stacked_df
    
    def request_query(self, query, exist_next=False):
        self.logger.info("{} - request query : {}".format(self.__class__.__name__, query))
        if exist_next is True:
            url = self.domain + query
        else:
            url = self.domain + "/search?q=" + query
        
        self.driver.get(url)
        if self.driver.page_source is not None:    
            html = self.driver.page_source
        else:
            html = None
            
        time.sleep(random.randint(RANDOM_MIN_SEC, RANDOM_MAX_SEC))
        return html
        
    @property
    def domain(self):
        return self._domain


    