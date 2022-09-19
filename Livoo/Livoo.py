import scrapy


class LivooSpider(scrapy.Spider):
    start_urls = ['https://www.livoo.fr/en/', "https://www.livoo.fr/fr/",
                  'https://www.livoo.fr/es/', 'https://www.livoo.fr/de/',
                  'https://www.livoo.fr/it/']

    name = 'livoo.fr'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for categ_sel in response.css('.all-items::attr(href)').getall():
            yield response.follow(categ_sel, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_url in response.css('.card-product a::attr(href)').getall():
            yield response.follow(prod_url, callback=self.parse_item)

        if response.css(".next.js-search-link"):
            url = response.css(".next.js-search-link::attr(href)").get()
            yield response.follow(url, callback=self.parse_listing)

    def parse_item(self, response, **kwargs):
        manual = dict()

        manuals = ["Manuale d'uso ", 'Manual de uso ',
                   'Bedienungsanleitung ', 'User manual']
        pdfs = response.css("a[href*='.pdf'] span::text").getall()
        pdf = [pp for pp in pdfs if pp in manuals]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.css('span::text').get()
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            manual['model'] = response.css('span[itemprop*="sku"]::text').get()
            breadcrumb = response.css('.breadcrumb--item span::text').getall()
            try:
                manual['product'] = breadcrumb[-1]
                manual['product_parent'] = breadcrumb[-2]
            except IndexError:
                self.logger.info('Product Not Found')
                continue
            manual['thumb'] = response.css(
                '.thumb.js-thumb::attr(data-image-large-src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Livoo"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def close(spider, reason):
        print(spider.rtypes)
