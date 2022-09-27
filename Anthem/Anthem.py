
import scrapy


class AnthemSpider(scrapy.Spider):
    start_urls = [
        'https://anthemav.com']
    name = 'anthemav.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for categ_sel in response.css('.col a::attr(href)').getall():
            url = response.urljoin(categ_sel)
            yield response.follow(url, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_sel in response.css(".prodbox a::attr(href)").getall():
            url = response.urljoin(prod_sel)
            yield response.follow(url, callback=self.parse_downloads)

    def parse_downloads(self, response):
        for download_sel in response.css(".contain-narrow.subnav a::attr(href)").getall():
            if '=reviews' in download_sel:
                url = response.urljoin(download_sel)
                yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):

        pdfs = response.css("#downloads")[1].css('a::text').getall()
        pdf = [pp for pp in pdfs if 'Manual' == self.clean_type(pp)]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('#downloads')[1].css('a'):
            manual = dict()
            rfile = pdf_sel.css("::attr(href)").get()
            # if rfile in self.rfiles:
            #     continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.css("::text").get())
            if not rtype:
                self.logger.info("No type found")
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype
            model = response.css('.modelInfo h1::text').get()
            if 'STR' in model:
                model = 'STR'
            manual['model'] = model
            manual['product'] = response.css('.desc a::text').getall()[-1]
            manual['thumb'] = response.urljoin(
                response.css('.contain-narrow img::attr(src)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Anthem"
            manual['product_lang'] = 'en'

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'manual' in rtype.lower() or 'user_manual' in rtype.lower():
            return "Manual"
        elif 'quick start guide' in rtype.lower() or 'qig' in rtype.lower():
            return "Quick Start Guide"
        elif 'datasheet' in rtype.lower() or 'data sheet' in rtype.lower():
            return "Data Sheet"
        elif 'technical drawings' in rtype.lower():
            return "Technical Drawings"
        elif 'instructions' in rtype.lower():
            return "Instructions"
        elif 'special order versions' in rtype.lower():
            return 'Special Versions'
        elif 'systems guide' in rtype.lower():
            return 'Systems Guide'
        elif 'brochure' in rtype.lower():
            return 'Brochure'
        elif 'review and award summary' in rtype.lower():
            return 'Review Summary'
        else:
            return ''

    def close(spider, reason):
        print(spider.rtypes)
