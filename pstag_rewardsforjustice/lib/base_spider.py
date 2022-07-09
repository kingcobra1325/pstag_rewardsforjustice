from datetime import datetime

import scrapy, json, re
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse

import traceback

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class BaseScrapySpider(scrapy.Spider):
    name = 'DefaultSpiderName'
    allowed_domains = []
    start_urls = []

    item_data_label = []
    meta_data = {}

    post_payload = {}

    json = json
    datetime = datetime
    ScrapyRequest = scrapy.Request
    FormRequest = scrapy.FormRequest
    HtmlResponse = HtmlResponse

    @staticmethod
    def perform_dob_regex(data):
        return re.compile(r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}|d{4}").findall(data)

    def start_requests(self):
        self.meta_data.update({
                    "spider_name":self.name,
                    "item_data_label":self.item_data_label,
                    })
        for url in self.start_urls:
            if not self.post_payload:
                yield self.ScrapyRequest(
                    url=url,
                    callback=self.initial_parse,
                    errback=self.errback_httpbin,
                    meta=self.meta_data)
            else:
                yield self.FormRequest(
                    url=url,
                    formdata=self.post_payload,
                    callback=self.initial_parse, 
                    errback=self.errback_httpbin,
                    meta=self.meta_data,
                )
    
    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
    
    def initial_parse(self, response):
        pass

    def copy_empty_results(self,item_data_label):
        empty_item_dict = {}
        # Create Empty Dict from Data
        for item in item_data_label:
            empty_item_dict.update({item:"null"})
        return empty_item_dict
    
    def load_item_from_dict(self,item_data,item_class):
        data = ItemLoader(item = item_class())
        for item_key in list(item_data):
            if item_data[item_key]:
                data_value = item_data[item_key]
            else:
                data_value = 'null'
            data.add_value(item_key,data_value)
        return data.load_item()
