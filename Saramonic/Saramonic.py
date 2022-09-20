import scrapy


class SaramonicSpider(scrapy.Spider):
    start_urls = ['https://www.saramonic.com/']
    name = 'saramonic.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for lang_sel in response.css('#xuanzhe option::attr(value)').getall():
            yield response.follow(lang_sel, callback=self.parse_categ)

    def parse_categ(self, response):
        for cat_sel in response.css('.menu-item-object-page.fusion-dropdown-submenu'):
            meta = dict()
            meta['product'] = cat_sel.css("span::text").get()
            meta['product_parent'] = cat_sel.xpath(
                './../..').css('span::text').get()
            url = cat_sel.css("a::attr(href)").get()
            yield response.follow(url, callback=self.parse_listing, meta=meta)

    def parse_listing(self, response):
        for prod_url in response.css(".fusion-fullwidth-2 .fusion-column-wrapper a::attr(href)").getall():
            yield response.follow(prod_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response, **kwargs):

        pdfs = response.css("a[href*='.pdf'] ::text").getall()
        pdf = [pp for pp in pdfs if 'manual' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            manual = dict()
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.css('::text').get())
            if not rtype:
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            model = response.css(
                '.fusion-column-wrapper h1::text').get()
            if not model:
                model = response.css(
                    '.fusion-column-wrapper h1 strong::text').get()
            manual['model'] = model
            manual['product'] = response.meta.get('product')
            manual['product_parent'] = response.meta.get('product_parent')
            try:
                thumb = response.css('.img-responsive::attr(src)').get()
                if not thumb:
                    thumb = response.css(".image img::attr(src)").get()
                manual['thumb'] = thumb
            except:
                self.logger.info("Thumb not found")
                continue
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Saramonic"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'user manual' in rtype.lower():
            return "User Manual"
        elif 'manual' in rtype.lower():
            return "Manual"
        else:
            return ''

    def close(spider, reason):
        print(spider.rtypes)
