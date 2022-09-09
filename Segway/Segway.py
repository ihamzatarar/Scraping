
import scrapy


class SegwaySpider(scrapy.Spider):
    name = 'segway.com'
    start_urls = ['https://segway.com/international']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for lang_sel in response.css('.item-country a::attr(href)').getall():
            yield response.follow(lang_sel, callback=self.parse_categ)

    def parse_categ(self, response):
        for prod in response.css(".mega-menu-product-link"):
            meta = dict()
            meta['model'] = prod.css('span::text').getall()[-1]
            product = prod.css("::attr(href)").get()
            if 'https:' not in product:
                url = response.urljoin(product)
            else:
                url = product
            yield response.follow(url, callback=self.parse_item, meta=meta)

    def parse_item(self, response, **kwargs):
        manual = dict()
        manuals = ['User Manual', 'Manual', 'User Instruction']
        pdfs = response.css(
            "a[href*='.pdf']").xpath('preceding-sibling::span[1]/text()').getall()
        pdf = [pp for pp in pdfs if self.clean_type(pp) in manuals]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.xpath(
                'preceding-sibling::span[1]/text()').get())
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            model = response.css('.h1::text').getall()
            manual['model'] = response.meta.get('model').replace(
                ' Powered by Segway', '').replace('Segway ', '')
            manual['product'] = 'No Category'
            manual['thumb'] = response.css(
                'img[src*="_product_full"]::attr(src)').get().replace('_full', '_overview')
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "segway.com"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'um' in rtype.lower() or 'CROATIAN' in rtype:
            return "User Manual"
        elif 'sm' in rtype.lower():
            return "Service & Maintenance"
        elif 'eu do c' in rtype.lower():
            return "Declaration of Conformity"
        elif ' d ' in rtype.lower() or ' e ' in rtype.lower():
            return "Important information"
        elif 'manual' in rtype.lower():
            return "Manual"
        elif 'user instruction' in rtype.lower() or 'user instruction' in rtype.lower():
            return "User Instruction"
        else:
            return rtype

    def close(spider, reason):
        print(spider.rtypes)
