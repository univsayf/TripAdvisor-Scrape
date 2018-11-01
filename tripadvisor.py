# -*- coding: utf-8 -*-
# spanish: filters_detail_language_filterLang_es
# portuguese: filters_detail_language_filterLang_pt
# German: filters_detail_language_filterLang_de
# Italian: filters_detail_language_filterLang_it
# French: filters_detail_language_filterLang_fr
# japanese: filters_detail_language_filterLang_ja
# Dutch: filters_detail_language_filterLang_nl


import csv
import logging
from time import sleep
from scrapy import Spider
from selenium import webdriver
from scrapy.http import Request
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class TripadvisorSpider(Spider):
    name = 'get_review_urls'
    allowed_domains = ['tripadvisor.com']
    start_urls = []

    with open('urls.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            start_urls.append(line[0])

    def __init__(self):
        logging.getLogger('selenium').setLevel(logging.WARNING)

        chromeOptions = webdriver.ChromeOptions()
        prefs = {'profile.managed_default_content_settings.images': 2}
        chromeOptions.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chromeOptions)

    def parse(self, response):
        # click on all languages label
        self.driver.get(response.url)
        sleep(5)

        self.driver.find_element_by_xpath('//label[@for="filters_detail_language_filterLang_ALL"]').click()
        sleep(15)

        sel = Selector(text=self.driver.page_source)
        review_tab = sel.xpath('//*[@class="ppr_rup ppr_priv_location_reviews_list_resp"]')
        review_urls = review_tab.xpath('.//*[@class="quote"]/a/@href|.//*[@class="quote isNew"]/a/@href').extract()
        for review_url in review_urls:
            yield {'review_url': response.urljoin(review_url)}

        while True:
            try:
                if 'class="nav next ui_button primary disabled"' in self.driver.page_source:
                    break

                # click on the next page
                self.driver.find_element_by_xpath('//a[text()="Next"]').click()
                sleep(3)

                sel = Selector(text=self.driver.page_source)
                review_tab = sel.xpath('//*[@class="ppr_rup ppr_priv_location_reviews_list_resp"]')
                review_urls = review_tab.xpath('.//*[@class="quote"]/a/@href|.//*[@class="quote isNew"]/a/@href').extract()
                for review_url in review_urls:
                    yield {'review_url': response.urljoin(review_url)}

            except NoSuchElementException:
                break

    # def close(self, reason):
    #     self.driver.quit()
