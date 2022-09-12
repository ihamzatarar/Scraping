import scrapy
import re


class InFocusSpider(scrapy.Spider):
    name = 'infocus.com'
    start_urls = ['https://infocus.com/projector-series/lightpro/', 'https://infocus.com/projector-series/quantum-laser/',
                  'https://infocus.com/product/quantum-led-professional-series/']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for prod_sel in response.css(".product-listing__item::attr(href)").getall():
            yield response.follow(prod_sel, callback=self.parse_item)
        if response.url == 'https://infocus.com/product/quantum-led-professional-series/':
            yield response.follow(response.url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        types_allowed = ['Users Guide',
                         'Quick Start Guide', 'Warranty Information']

        pdfs = response.css("a[href*='.pdf']").xpath(
            './../../preceding-sibling::p[1]/text()').getall()
        pdf = [pp for pp in pdfs if pp.strip() == 'Users Guide' or pp.strip()
               == 'Quick Start Guide']
        if not pdf:
            self.logger.warning("No manual found")
            return

        product_info = response.css('[product-id]').get()
        try:
            models = list(re.findall(r'"title":"(\w*)"', product_info))
        except (AttributeError, IndexError):
            self.logger.info('model not found')
            return
        for model in models:
            for pdf_sel in response.css('a[href*=".pdf"]'):
                manual = dict()
                rtype = pdf_sel.xpath(
                    './../../preceding-sibling::p[1]/text()').get().strip()
                if rtype in types_allowed:
                    rfile = pdf_sel.css("::attr(href)").get()
                    self.rfiles.add(rfile)
                    self.rtypes.add(rtype)
                    manual['file_urls'] = [rfile]
                    manual['type'] = rtype
                    try:
                        thumb = re.search(
                            r'thumb":"(.*)', product_info).group(1).split('"')[0]
                    except (AttributeError, IndexError):
                        self.logger.info('Thumb not found')
                        continue
                    breadcrumbs = response.css(
                        '.breadcrumbs__item a::text').getall()
                    manual['model'] = breadcrumbs[2].strip() + ' ' + model
                    manual['model_2'] = model
                    manual['product'] = breadcrumbs[1].strip()
                    manual['thumb'] = thumb
                    manual['url'] = response.url
                    manual['source'] = self.name
                    manual['brand'] = "InFocus"
                    manual['product_lang'] = response.css(
                        'html::attr(lang)').get().split('-')[0]

                    yield manual
