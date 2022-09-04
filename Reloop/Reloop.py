import scrapy


class ReloopSpider(scrapy.Spider):
    name = 'reloop.com'
    start_urls = ['https://www.reloop.com/products#']
    rfiles = set()
    rtypes = set()

    # For All languages
    # def parse(self, response):
    #     for lang_sel in response.css('#select-language option::attr(value)').getall():
    #         yield response.follow(lang_sel, callback=self.parse_categ)

    def parse(self, response):
        for categ_sel in response.css('.inner'):
            meta = dict()
            meta['product'] = categ_sel.css('h2::text').get()
            url = categ_sel.css('a::attr(href)').get()
            yield response.follow(url, callback=self.parse_product, meta=meta)

    def parse_product(self, response):
        for prod in response.css(".inner"):
            url = prod.css("a::attr(href)").get()
            yield response.follow(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response, **kwargs):
        manual = dict()

        pdfs = response.css("a[href*='.pdf'] span::text").getall()
        pdf = [pp for pp in pdfs if self.clean_type(
            pp) == 'Instruction Manual']
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.css('span::text').get())
            if not rtype:
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype
            manual['model'] = response.css('.product-name h1::text').get()
            manual['product'] = response.meta.get('product')
            manual['thumb'] = response.css(
                '.list-group-item[href*=".jpg"]::attr(href)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Reloop"
            manual['product_lang'] = response.css(
                '.current-language::text').get()

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'Quickstart' in rtype or 'Quick-Start' in rtype or 'Quick Start Guide' in rtype:
            return 'Quick Start Guide'
        elif 'Instruction Manual' in rtype:
            return 'Instruction Manual'
        elif 'MIDI Map' in rtype:
            return 'MIDI Map'
        elif 'Comparison Chart' in rtype or 'comparison chart' in rtype:
            return 'Comparison Chart'
        elif 'Compatibility chart' in rtype or 'compatibility chart' in rtype:
            return 'Compatibility Chart'
        elif 'Platter Play Mode' in rtype:
            return 'Platter Play Mode'
        elif "What's new?" in rtype or 'How to' in rtype:
            return None
        elif '-' in rtype:
            return rtype.split('-')[1].strip()
        else:
            return rtype.strip()

    def close(spider, reason):
        print(spider.rtypes)
