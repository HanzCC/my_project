import re 
from urllib import robotparser
# from urllib.parse import urljoin
import requests
from lxml.html import document_fromstring
import pandas as pd
from datetime import date
import json

class web_crawler():
    def __init__ (self, base_url):
        my_header = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
            }
        self.header = my_header
        self.base_url = base_url


    def robot_files_reader(self, robotTxt='robots.txt'):
        robot_url = self.base_url + robotTxt
        rp = robotparser.RobotFileParser()
        rp.set_url(robot_url)
        rp.read()
        return rp.can_fetch(self.header, self.base_url)

    def request_response(self, proceed_to_scrape='Y'):
        allow_to_scrape = self.robot_files_reader()
        if not allow_to_scrape:
            proceed = proceed_to_scrape
        if proceed == "Y":
            try:
                r = requests.get(url=self.base_url, headers=self.header)
                status_code = r.status_code
                if status_code == 200:
                    html = r.text
                    print("Download success, status code: ", status_code)
                elif status_code >= 400:
                    print("Download Error", r.text)
            except requests.exceptions.RequestException as e:
                print("Download Error", e)
                html = None
            return html
        else:
            html = None
            return html


    # def crawl_links(self, htmls=False, equities=False):
    #     webpage_link_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    #     html = self.request_response()
    #     html_links = webpage_link_regex.findall(html)
        
    #     equities_links = []
    #     for link in html_links:
    #         if "'/trade/trading_resources/listing_directory/company-profile" in link:
    #             equities_links.append(link)          
    #     if equities:
    #         return equities_links
    #     if htmls:
    #         return html_links

    def extract_data(self, xpath, class_element):
        html = self.request_response()
        doc = document_fromstring(html)
        div = doc.xpath(xpath)
        HtmlElement = div.pop()
        extract = HtmlElement.find_class(class_element)
        DATA = []
        for d in extract:
            content = re.sub('\n', "", d.text_content())
            DATA.append(content)
        return doc, DATA

    def build_frame(self, xpath, class_element):
        _, DATA = self.extract_data(xpath, class_element)
        data_title = DATA[:5]
        data_content = DATA[5:]
        # DICT = title
        DICT = {}
        for i, key in enumerate(data_title):
            DICT[key] = data_content[i::5]
            i+=1
        return DICT

if __name__ == '__main__':
    bursa_111122 = web_crawler(base_url='https://www.bursamalaysia.com/')
    doc = bursa_111122.request_response()
    todate = date.today().isoformat()
    Date = {}
    Date[todate]= {}
    Date[todate]["Most_Active"] =  bursa_111122.build_frame("""//div[@id="pills-active"]""", 'text-center')
    Date[todate]['Top_Gainer'] = bursa_111122.build_frame("""//div[@id="pills-gainer"]""", 'text-center')
    Date[todate]['Top_Loser'] = bursa_111122.build_frame("""//div[@id="pills-loser"]""", 'text-center')
    fname = (f'bursa_{todate}.json')
    with open (fname, 'w', encoding='utf-8') as f:
        json.dump(Date, f)
        f.write(doc)