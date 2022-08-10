from distutils.log import info
import scrapy
from scrapy.spiders import SitemapSpider


class NelsonirrigationSpider(SitemapSpider):
    name = 'nelsonirrigation.com'
    sitemap_urls = ['https://nelsonirrigation.com/sitemap.xml']
    sitemap_rules = [('/products/','parse')]
    rfiles = set()

    def parse(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = response.urljoin(rfile)

            try:
                for tab in response.css('.library-category'):
                    for url in tab.css('a[href*=".pdf"]::attr(href)').getall():
                        if url == rfile :
                            manual['type'] = tab.css(' .library-category-head::text').get().strip()
                            if not manual['type']:
                                return
            except:
                self.logger.info('Type Not found')
                return
            
            manual['model'] = response.css('h1.product-name::text').get()
            if not manual['model']:
                return
            try:
                manual['product'] = response.css('.product-text a::text').getall()[-1]
            except IndexError:
                self.logger,info('Product Not Found')
                return
            manual['thumb'] = response.css('.product-image img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Nelson"
            manual['product_lang'] = response.css('html::attr(lang)').get()

            yield manual
