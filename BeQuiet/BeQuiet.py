#from manual_scraper_ext.items import Manual

import scrapy


class BeQuietSpider(scrapy.Spider):
    name = 'bequiet.com'
    start_urls = ['https://www.bequiet.com/cz/', 'https://www.bequiet.com/de/',
                  'https://www.bequiet.com/en/', 'https://www.bequiet.com/es/',
                  'https://www.bequiet.com/fr/', 'https://www.bequiet.com/hu/',
                  'https://www.bequiet.com/pl/', 'https://www.bequiet.com/ru/',
                  'https://www.bequiet.com/tw/', 'https://www.bequiet.com/ua/',
                  ]
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for cat_sel in response.css('.is-active_ a::attr(href)').getall():
            url = response.urljoin(cat_sel)
            yield response.follow(url, callback=self.parse_variant)

    def parse_variant(self, response):
        for prod_url in response.css('.btn.btn-std.product-variant::attr(href)').getall():
            url = response.urljoin(prod_url)
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        manuals = [' Manuál', ' Handbuch', ' Manual', ' Manuel', ' Útmutató',
                   ' Instrukcja obsługi', ' Руководство пользователя', ' 說明書', ' Інструкція користувача']
        pdfs = response.css(
            'h3+ .highlight-background--alternative a::text').getall()
        pdf = [pp for pp in pdfs if pp in manuals]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('h3+ .highlight-background--alternative a'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.css("::text").get().strip()
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype
            breadcrumb = response.css('.breadcrumb-item span::text').getall()
            manual['model'] = breadcrumb[1] + '' + breadcrumb[2]
            manual['model_2'] = breadcrumb[3].replace('| ', '')
            manual['product'] = breadcrumb[0]
            manual['thumb'] = response.urljoin(response.css(
                '.series--image.m-left source::attr(srcset)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Be Quiet!"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def close(spider, reason):
        print(spider.rtypes)
