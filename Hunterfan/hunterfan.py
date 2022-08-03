import scrapy
import re
from scrapy.spiders import SitemapSpider



class HunterfansSpider(SitemapSpider):
    name = 'hunterfan.de'
    sitemap_urls = ['https://hunterfan.de/sitemap.xml']
    rfiles = set()

    sitemap_rules = [('/products/','parse')]

    def parse(self, response,**kwargs):
        manual = dict()

        for pdf_sel in response.css('a[href*=".pdf"]'):
           rfile = pdf_sel.css("::attr(href)").get()
           if rfile in self.rfiles:
            continue
           self.rfiles.add(rfile)
           manual['file_urls'] = rfile   
           manual['type'] = 'Operating Manual'
           manual['brand'] = response.css('.vendor a::text').get()
           manual['url'] = response.url
           manual['product'] = "Ceiling Fan"
           manual['product_lang'] = response.css('html').attrib['lang']
           thumb = response.css('div.gallery-cell a::attr(href)').get()
           manual['thumb'] = response.urljoin(thumb)
           manual['source'] = self.name
           title = response.css('.product_name::text').get()
           try:
               manual['model']= re.search(r'Fan\b(.*)\b\d',title).group(1)
           except:
               self.logger.info("Model not found")
               return
         
           yield manual

        

