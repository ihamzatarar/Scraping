from itertools import product
import scrapy

class MaxxworldSpider(scrapy.Spider):
    name = 'maxx-world.de'
    start_urls = ['https://www.maxx-world.de/gourmetmaxx-kuechenmaschine-6-geschwindigkeitsstufen-und-turbofunktion-rot']
    rfiles = set()


    def parse(self, response):
        for brand_sel in response.css('.level0.nav-submenu.nav-panel--dropdown.nav-panel li a'):
            meta = dict()
            meta['brand'] = brand_sel.css("span::text").get()
            url = brand_sel.css("::attr(href)").get()
            yield response.follow(url, callback=self.parse_listing, meta=meta)

    def parse_listing(self, response):
        for prod_url in response.css('.product-name a::attr(href)').getall():
            yield response.follow(prod_url, callback=self.parse_item, meta=response.meta)

        if response.css('.next'):
            next_page = response.css('.next a::attr(href)').get()
            yield response.follow(next_page, callback=self.parse_listing,meta=response.meta)

    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = pdf_sel.xpath("./..").css('p::text').get()
            manual['model'] = response.css('.value::text').get()
            brand = response.meta.get('brand')
            manual['brand'] = brand
            try:
                title =  response.css('h1::text').get().replace(brand,'')
                prod = title.replace(brand.lower(),'')
                if '-' in prod:
                    prod = prod.split('-')[0]
                manual['product'] = prod
            except IndexError:
                continue
            manual['thumb'] = response.css('.product-image.zoom-inside a::attr(href)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = response.meta.get('brand')
            manual['product_lang'] = response.css('html::attr(lang)').get()

            yield manual
