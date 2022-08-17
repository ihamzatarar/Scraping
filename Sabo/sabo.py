from manual_scraper_ext.items import Manual

class SaboSpider(scrapy.Spider):
    name = 'sabo-online.de'
    start_urls = [
        'https://sabo-online.com/en/service/',
                  'https://sabo-online.com/service/',
                  'https://sabo-online.com/fr/service-clientele/'
    ]
    rfiles = set()
    rtypes = set()

    def parse(self, response, **kwargs):
        for pdf_sel in response.css('a[href*=".pdf"]'):
            manual = Manual()
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = rfile
            product = pdf_sel.css('a[href*=".pdf"]').xpath('./../../../../../../../..').css('h3::text').get()
            excluded_products = ['Akkus & Ladegeräte','Battery data sheet']
            if product in excluded_products:
                continue
            manual['product'] = product
            if '/en/' in response.url:
                manual['type'] = 'Instruction Manual'
            elif '/fr/' in response.url :
                manual['type'] = 'Modes d’emploi'
            else:
                manual['type'] = 'Gebrauchsanleitungen'
            manual['model'] = pdf_sel.css("::text").get().replace('SABO ','')
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "SABO"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            self.rtypes.add(manual['type'])
            yield manual

    def close(spider, reason):
        print(spider.rtypes)