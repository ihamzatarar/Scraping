import scrapy
import re
from scrapy.spiders import SitemapSpider



class Manual(scrapy.Item):

     model = scrapy.Field()
     brand = scrapy.Field()
     product = scrapy.Field() 
     product_lang = scrapy.Field()
     file_urls  = scrapy.Field() 
     Type = scrapy.Field()
     url  = scrapy.Field()
     thumb = scrapy.Field()
     source = scrapy.Field()


class ScarlettSpider(SitemapSpider):
    name = 'scarlett.ru'
    sitemap_urls = ['https://www.scarlett.ru/sitemap.xml']
    start_urls = ['https://www.scarlett.ru/sitemap.xml']

    def parse(self, response):

        manual = Manual()

        manual['model'] = response.xpath('//*[@class="product-card__option-value product-card__option-value_uppercase"]/text()').get()
        manual['brand'] = re.search(r'(\w*)\s.\s',response.css('p.footer__copyright::text').get()).group(1)

        try:
            manual['product'] = re.search(r'\s(\w.*)',response.css('h1::text').get()).group(1)
        except:
            return
        manual['product_lang'] = re.search(r'(\w*)\-',response.css('html').attrib['lang']).group(1)
        try:
            pdfs = response.xpath('//*[@class="product-tabs__materials__download"]/@href').getall()
            if pdfs == []:
                return
            manual['file_urls'] = list(map(lambda x : self.name + x,pdfs))
        except:
            return
        manual['Type'] = response.css('span.product-tabs__materials__download-text::text').getall()
        manual['thumb'] = response.xpath('//html/head/meta[@itemprop="image"]/@srcset').get()
        manual['url'] = response.url
        manual['source'] = self.name

        yield manual





