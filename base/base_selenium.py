import time
from selenium import webdriver
from fake_useragent import UserAgent
from abc import abstractmethod

class BaseSelenium(object):
    def __init__(self, logger, is_proxy=False):
        self.logger = logger
        self.is_proxy = is_proxy
        self.initialize(is_proxy=self.is_proxy)
        
    def initialize(self, is_proxy, restart=False) -> None:
        if restart is False:
            ua = UserAgent()
            self.random_ua = ua.random
            self.logger.info("set random agent ({})".format(self.random_ua))
            
        self.options = webdriver.ChromeOptions()
        if is_proxy is True:
            message = "proxy options is {}." \
                    "If the proxy option is True, you must be start proxy server before this script." \
                    .format(is_proxy)
            self.logger.warning(message)
            self.options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
        
        self.options.add_argument(f"--user-agent={self.random_ua}")
        self.options.add_argument(f"--app-version={self.random_ua}")
        
        self.driver = webdriver.Chrome(options=self.options)
        if is_proxy is False:
            self.set_driver()
            
    def set_driver(self) -> None:
        self.driver.implicitly_wait(8)          # page load에 걸리는 시간
        self.driver.set_page_load_timeout(8)    # element load에 걸리는 시간 제한
        self.driver.set_script_timeout(8)       # script load에 걸리는 시간 제한
        
    def restart(self):
        self.driver.quit()
        time.sleep(1)
        self.initialize(self.is_proxy, restart=True)
    
    def get_url(self, url):
        html = None
        try:
            self.driver.get(url)
            html = self.driver.page_source
        except KeyboardInterrupt as e:
            self.restart()
        except:
            pass
        return html
    
    def labeling(self, urls):
        def label():
            result = None
            while result != 'f' and result != 't':
                result = str(input("'t' or 'f' >> "))
            return result
        
        results = []
        for idx, url in enumerate(urls):
            try:
                print(f"({idx+1}/{len(urls)}) ", end=' ')
                self.get_url(url)
                results.append((url, label()))
            except KeyboardInterrupt as e:
                print('\n')
                self.restart()
                break
        return results
    
    
    @abstractmethod
    def request_query(self, *inputs):
        raise NotImplementedError