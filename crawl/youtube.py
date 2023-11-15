import time
import random
import pandas as pd
from base import BaseSelenium
from bs4 import BeautifulSoup
from task.tasks import YoutubeTask
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


RANDOM_MIN_SEC = 15
RANDOM_MAX_SEC = 20


class YoutubeSelenium(BaseSelenium):
    def __init__(self, config, logger, is_proxy):
        super().__init__(logger, is_proxy)
        self.task = YoutubeTask(config)
        self.queries = self.task.queries
        self.logger = logger
        self._domain = "https://www.youtube.com"
    
    def __call__(self, html) -> pd.DataFrame:
        # self._filter()
        self._scroll()
        
        df = pd.DataFrame(columns=["title", "content", "url", "user_t", "user_c"])
        
        pages = self.driver.find_elements(
            By.XPATH, 
            "//a[@id='video-title']"
        )
        if len(pages) == 0:
            return df
        
        for page in pages:
            row = self.task.run(page)
            df.loc[len(df), :] = row    # 데이터 삽입
            
        return df
    
    def request_query(self, query):
        # https://www.youtube.com/results?search_query=부결db
        url = self.domain + "/results?search_query=" + query
        self.driver.get(url)
        
        if self.driver.page_source:
            html = self.driver.page_source
        else:
            html = None
        
        time.sleep(random.randint(RANDOM_MIN_SEC, RANDOM_MAX_SEC))            
        return html
        
    def _filter(self) -> None:
        filter_button = self.driver.find_elements(
            By.XPATH, 
            "//button[@class='yt-spec-button-shape-next yt-spec-button-shape-next--text yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-trailing ']"
        )[0]
        filter_button.send_keys(Keys.ENTER)
        time.sleep(1)
        
        upload_dates = self.driver.find_elements(
            By.XPATH,
            "//a[@class='yt-simple-endpoint style-scope ytd-search-filter-renderer']"
        )[:5]
        time.sleep(1)
        at_month = upload_dates[3]
        at_month.send_keys(Keys.ENTER)
        time.sleep(1)
        return
    
    def _scroll(self) -> None:
        last_page_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);"
            )
            time.sleep(random.randint(1, 3))
            self.driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight-50)"
            )
            time.sleep(random.randint(1, 3))
            new_page_height = self.driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
            if new_page_height == last_page_height:
                break
            else:
                last_page_height = new_page_height
        return
    
    @property
    def domain(self):
        return self._domain