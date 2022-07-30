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


class HunterfansSpider(SitemapSpider):
    name = 'hunterfan.de'
    sitemap_urls = ['https://hunterfan.de/sitemap.xml']
    start_urls = ['https://hunterfan.de/sitemap.xml']
    pdffiles = set()

    sitemap_rules = [('/products/','parse')]

    def parse(self, response,**kwargs):
        manual = Manual()
        manual['brand'] = response.css('.vendor a::text').get()
        manual['url'] = response.url
        manual['product_lang'] = response.css('html').attrib['lang']
        manual['thumb'] = 'http:' + response.xpath('//*[@class="gallery-cell"]/a/@href').get()
        manual['source'] = self.name
        title = response.css('.product_name::text').get()
        manual['product'] = "Ceiling Fan"
        try:
            Check = False
            for i in response.css('a[href*=".pdf"]'):
                if i.css('::text').get() == 'Please click here.'or i.css('::text').get() == 'Hier klicken zum öffnen'or i.css('::text').get() == 'Click here to open':
                    file_url = re.search(r'(http.*)\"\s',i.get()).group(1)
                    manual['file_urls'] = file_url
                    manual['Type'] = 'Operating Manual'
                    Check = True
            if not Check:
                return
        except:
            return
        try:
            manual['model']= re.search(r'Fan\b(.*)\b\d',title).group(1)
        except:
            return

        yield manual
        

