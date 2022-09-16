import scrapy


class SinboSpider(scrapy.Spider):
    name = 'sinbo.com.tr'
    start_urls = ['http://www.sinbo.com.tr/en']
    rfiles = set()
    rtypes = set()
    custom_settings = {
        'CONCURRENT_REQUESTS': 5,
        "DOWNLOAD_DELAY": 2,
    }

    def parse(self, response):
        for categ_sel in response.css('.sub2 a::attr(href)').getall():
            url = response.urljoin(categ_sel)
            yield response.follow(url, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_sel in response.css('.images a::attr(href)').getall():
            url = response.urljoin(prod_sel)
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.css('span::text').get().strip()
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            model = response.css(
                '.col-md-4.col-xs-12.col-sm-12.pa h3::text').get()
            product = response.css(
                '.col-md-4.col-xs-12.col-sm-12.pa h1::text').get()
            manual['model'] = model
            manual['product'] = self.clean_product(product, model)
            manual['thumb'] = response.css('.images img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Sinbo"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_product(self, product, model):
        m = model.replace('-', ' ')
        p = product.replace('-', ' ')
        if m in p:
            return p.replace(m, '')
        else:
            return product

    def close(spider, reason):
        print(spider.rtypes)
