import scrapy


class NebulaSpider(scrapy.Spider):
    start_urls = [
        'https://us.seenebula.com/collections/go-anywhere-series/products/d2421']
    name = 'seenebula.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for lang_sel in response.css('.coutriesSwitch a::attr(href)').getall():
            yield response.follow(lang_sel, callback=self.parse_prod)

    def parse_prod(self, response):
        for prod_sel in response.css(".mega-menu__content a::attr(href)").getall():
            if 'https' in prod_sel:
                url = prod_sel
            else:
                url = response.urljoin(prod_sel)
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        pdfs = response.css(".col.down a").xpath(
            './../..').css('span::text').getall()
        pdf = [pp for pp in pdfs if pp.lower().strip() == 'manual']
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('.col.down a'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.xpath(
                './../..').css('span::text').get().strip())
            if not rtype:
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            manual['model'] = response.css('.product_name.title::text').get()
            manual['product'] = response.css(
                'title::text').get().split('|')[-1]
            manual['thumb'] = response.urljoin(response.css(
                '.product-gallery__link::attr(href)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Nebula"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'declaration of conformity' in rtype.lower() or 'software' in rtype.lower():
            return ""
        else:
            return rtype

            def close(spider, reason):
                print(spider.rtypes)
