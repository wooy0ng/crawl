import re
import pandas as pd
from base import BaseTask

class YoutubeTask(BaseTask):
    def __init__(self, config):
        super().__init__(config)
        self._current_data = None
    
    def run(self, page) -> pd.Series:
        url = page.get_attribute('href')
        title = page.text
        
        return pd.Series({
            "title": title,
            "content": '',
            "url": url,
            "user_t": self.get_user(title),
            "user_c": ''
        })
    
    @staticmethod
    def get_user(text):
        try:
            text = re.sub(r"[^A-Za-z0-9가-힣\s@]", ' ', text)
            user = re.findall(r"@\w{5,}", text)[0]   # 아이디 부분만 추출
        except:
            user = ""
        return user 


class GoogleTask(BaseTask):
    def __init__(self, config):
        super().__init__(config)
        self._current_data = None
    
    def run(self, soup) -> pd.DataFrame:
        titles, contents = self.get_titles_contents(soup)
        urls = self.get_urls(soup)
        users_in_title = self.get_users(titles)
        users_in_content = self.get_users(contents)
        
        self._current_data = pd.DataFrame({
            'title': titles,
            'content': contents,
            'url': urls,
            'user_t': users_in_title,
            'user_c': users_in_content
        })
        return self.current_data
    
    @staticmethod
    def get_titles_contents(soup):
        titles, contents = [], []
        fs = soup.find_all("div", attrs={"data-snf": "x5WNvb"})
        for f in fs:
            title = f.find("h3").string
            content = ''
            if content:=f.parent.find("div", attrs={"data-snf": "nke7rc"}):
                content = content.text
            titles.append(title)
            contents.append(content)
        return titles, contents
    
    @staticmethod
    def get_users(lists):
        users = []
        for text in lists:
            try:
                text = re.sub(r"[^A-Za-z0-9가-힣\s@]", ' ', text)
                user = re.findall(r"@\w{5,}", text)[0]   # 아이디 부분만 추출
            except:
                user = ""
            users.append(user)
        return users
    
    @staticmethod
    def get_urls(soup):
        urls = []
        fs = soup.find_all("div", attrs={"data-snf": "x5WNvb"})
        for f in fs:
            href = f.find("a")["href"]
            urls.append(href)
        return urls
    
    @property
    def current_data(self):
        return self._current_data
    
    

