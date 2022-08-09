
import scrapy
import re
from scrapy.spiders import SitemapSpider

class niceboySpider(SitemapSpider):
    name = 'niceboy.eu'
    sitemap_urls = ['https://niceboy.eu/_sitemap-product.xml']
    sitemap_rules = [('/en/product/','parse')]
    rfiles = set()
   
    def parse(self, response): 
        for prod in response.css('.hover-underline::attr(href)').getall():
            meta = dict()
            meta['product'] = response.css('.breadcrumb-content.text-left a::text').getall()[-1]
            url = response.urljoin(prod)
            yield response.follow(url, callback=self.parse_item, meta=meta)

    def parse_item(self, response,**kwargs):
        manual = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = response.urljoin(rfile)
            try:
                for tab in response.css('div.feature-content'):
                    if tab.css('a::attr(href)').get() == rfile:
                        manual['type'] = re.match(r'\w*\b',tab.css('h3::text').get()).group(0)
            except (AttributeError,TypeError):
                self.logger.info("Type not found")
                return 
            try:
                manual['model'] = response.css('h2.mb-20::text').get()
                if not manual['model']:
                    return
            except:
                self.logger.info("Model not found")
                return
            manual['product'] = response.meta.get('product')
            manual['thumb'] = response.urljoin(response.css('.review-img img::attr(src)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Niceboy"
            manual['product_lang'] = response.css('html::attr(lang)').get()

            yield manual