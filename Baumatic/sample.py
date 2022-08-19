import logging

import scrapy


logger = logging.getLogger(__name__)


class BaumaticComAuSpider(scrapy.Spider):
    name = 'baumatic.com.au'
    allowed_domains = ['baumatic.com.au']
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }
    start_urls = [
        "https://www.baumatic.com.au/"
    ]

    def parse(self, response):
        for cat_sel in response.css(".v320-1.v720-1-of-5").xpath(
                ".//*[@class='list-title'][contains(text(), 'App')]/..//a"):
            meta = dict()
            meta['product'] = cat_sel.css("::text").get()
            url = cat_sel.css("::attr(href)").get()
            yield response.follow(url, callback=self.parse_listing, meta=meta)

    def parse_listing(self, response):
        for prod_url in response.css(".product-box .product-name a::attr(href)").getall():
            yield response.follow(prod_url, callback=self.parse_listing, meta=response.meta)

        if response.css("a[href$='.pdf']"):
            yield from self.parse_item(response)

    def parse_item(self, response, **kwargs):
        pdfs = response.css("a[href*='.pdf']::text").getall()
        pdf = [pp for pp in pdfs if 'manual' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdfs_div in response.css("a[href$='.pdf']"):
            manual = Manual()
            manual['file_urls'] = [pdfs_div.css('::attr(href)').get().strip()]
            manual['type'] = pdfs_div.css('::text').get().title()
            manual['brand'] = 'Baumatic'
            manual['source'] = self.name
            manual['url'] = response.url
            manual['product_lang'] = response.css("html::attr(lang)").get()
            manual['thumb'] = response.css(".product-image img::attr(src)").get()
            manual['model'] = response.css(".h3::text").get().strip().split("|")[-1].strip()
            manual['product'] = response.meta.get('product')
            yield manual


