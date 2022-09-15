from curses import meta
from re import M
import scrapy


class TranscendSpider(scrapy.Spider):
    name = 'transcend-info.com'
    start_urls = [
        'https://www.transcend-info.com/']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for categ in response.css('.List a'):
            meta = dict()
            meta['product'] = categ.css('::text').get()
            url = response.urljoin(categ.css('::attr(href)').get())
            yield response.follow(url, callback=self.parse_prod, meta=meta)

    def parse_prod(self, response):
        for prod_sel in response.css('.product_list_compare.More_Compare a::attr(href)').getall():
            url = response.urljoin(prod_sel)
            yield response.follow(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response, **kwargs):
        manual = dict()

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.css('h2::text').get()
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            manual['model'] = response.css(
                '.product_general_intro h2::text').get().strip()
            manual['product'] = response.meta.get('product')
            manual['thumb'] = response.css('.item img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Transcend"
            manual['product_lang'] = 'en'

            yield manual

            if response.css("#Content_PL_Support").getall():
                meta = dict()
                meta['manual'] = manual
                url = response.urljoin(response.css(
                    '#Content_PL_Support a::attr(href)').get())
                yield response.follow(url, callback=self.parse_support, meta=meta)

    def parse_support(self, response, **kwargs):

        pdfs = response.css(
            '.BTNs.BTN-Download').xpath('./../preceding-sibling::li/text()').getall()
        pdf = [pp for pp in pdfs if 'manual' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        manual = response.meta['manual']
        for pdf_sel in response.css('.BTNs.BTN-Download'):
            rtype = pdf_sel.xpath(
                './../preceding-sibling::li/text()').get()
            if not rtype:
                continue
            rfile = response.urljoin(pdf_sel.css('a::attr(href)').get())
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif "user's manual" in rtype.lower():
            return "User's Manual"
        elif 'manual' in rtype.lower():
            return "Manual"
        else:
            return ''
