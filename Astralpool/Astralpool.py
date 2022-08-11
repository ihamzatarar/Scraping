import scrapy
import re
from string import digits

class AstralpoolSpider(scrapy.Spider):
    name = 'astralpool.com'
    start_urls = ['https://www.astralpool.com/en/']
    rfiles = set()
    type = ''

    def parse(self, response):
        for cat_sel in response.css('#genux-menu-widget a::attr(href)').getall():
            url = cat_sel
            yield response.follow(url, callback=self.parse_listing)
    
    def parse_listing(self, response):
        for prod_url in response.css('#genux-category-products a::attr(href)').getall():
            yield response.follow(prod_url, callback=self.parse_listing)

        if response.css("a[href$='.pdf']"):
            yield from self.parse_item(response)

    
    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile) 
            manual['file_urls'] = rfile
            try:
                doc_type = pdf_sel.xpath('./../preceding-sibling::div[1]/text()').get()
                if doc_type != ' ':
                     self.type = doc_type
                     manual['type']= doc_type
                else:
                    manual['type']= self.type
            except:
                self.logger.info('Type Not Found')
                return
           
            manual['model'] = response.css('h1 span::text').get()
            try:
                manual['product'] = response.css('.genux-breadcrump a::text').getall()[2]
            except IndexError:
                return
            manual['thumb'] =  response.css('.genux-gallery-popup::attr(href)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "AstralPool"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            yield manual

