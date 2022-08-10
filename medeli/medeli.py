import scrapy
import re

class medeliSpider(scrapy.Spider):
    name = 'medeli.eu'
    start_urls = ['https://medeli.eu/products.html?preview=front']
    rfiles = set()

    def parse(self, response):
        for prod in response.css('.add-to-cart::attr(href)').getall():
            yield response.follow(prod, callback=self.parse_item)
        for next_page in response.css('.pagination.nobottommargin a'):
            if next_page.css('::text').get() == '»':
                next_page_url = next_page.css('::attr(href)').get()
                yield response.follow(next_page_url,callback=self.parse)
        

    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('[id="tabs-3"] a'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = rfile
            try:
                manual['type'] = re.match(r'\w*\s\w*\s(\w*)',pdf_sel.css('::text').get()).group(1).capitalize()
                if not manual['type']:
                    return
            except AttributeError:
                self.logger.info('Type Not Found')
                return
            manual['model'] = response.css('h1::text').get()
            try:
                manual['product'] = response.css('.breadcrumb a::text').getall()[-1].capitalize()
            except IndexError:
                self.logger.info('Product Not Found')
                return
            manual['thumb'] = response.css('.slide img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Medeli"
            manual['product_lang'] = response.css('[property="og:locale"]::attr(content)').get().split('-')[0]

            yield manual

