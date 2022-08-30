import scrapy
#from manual_scraper_ext.items import Manual


class NetisSystemsSpider(scrapy.Spider):
    name = 'netis-systems.com'
    start_urls = ['https://netis-systems.com/Global/index.html']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for lang_sel in response.css('.f16.b2 a::attr(href)').getall():
            yield response.follow(lang_sel, callback=self.parse_categ)

    def parse_categ(self, response):
        for cat_sel in response.css('.f13.tc h3 a'):
            meta = dict()
            try:
                meta['product_lang'] = response.css(
                    'html::attr(lang)').get().split('-')[0]
            except AttributeError:
                self.logger.warning('No language found')
            meta['product'] = cat_sel.css("::text").get()
            url = cat_sel.css("::attr(href)").get()
            yield response.follow(url, callback=self.parse_listing, meta=meta)

    def parse_listing(self, response):
        for prod_url in response.css('.a2 a::attr(href)').getall():
            yield response.follow(prod_url, callback=self.parse_download, meta=response.meta)

        if response.css('.prev::attr(href)').get():
            url = response.urljoin(response.css('.prev::attr(href)').get())
            yield response.follow(url, callback=self.parse_listing, meta=response.meta)

    def parse_download(self, response):
        url = response.urljoin(response.css(
            '.f16.r.b1 a::attr(href)').get())
        yield response.follow(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('h3.hide'):
            rfile = pdf_sel.css("a::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.xpath('preceding-sibling::p[1]/text()').get()
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype
            manual['model'] = response.css('h3.f24.c333::text').get()
            manual['product'] = response.meta.get('product')
            manual['thumb'] = response.urljoin(
                response.css('.l.img img::attr(src)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Netis"
            manual['product_lang'] = response.meta.get('product_lang')

            yield manual

    def close(spider, reason):
        print(spider.rtypes)
