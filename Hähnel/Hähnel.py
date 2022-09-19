import scrapy


class HähnelSpider(scrapy.Spider):
    start_urls = [
        'https://www.hahnel.com.au/']
    name = 'hahnel.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for categ_sel in response.css('.first .lev2 a::text').getall():
            url = response.urljoin(categ_sel)
            yield response.follow(url, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_sel in response.css(".product_box::attr(href)").getall():
            url = response.urljoin(prod_sel)
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        pdfs = response.css('.tab-container .copy a::text').getall()
        pdf = [pp for pp in pdfs if 'manual' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('.tab-container .copy a'):
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
            manual['model'] = self.clean_model(
                response.css('#pageTitle::text').get())
            manual['product'] = response.css('.folder a::text').getall()[2]
            manual['thumb'] = response.css('.item.zoom img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Hähnel"
            manual['product_lang'] = 'en'

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'manual' in rtype.lower() or 'user_manual' in rtype.lower():
            return "Manual"
        elif 'brochure' in rtype.lower() or 'qig' in rtype.lower():
            return "Brochure"
        elif 'doc' in rtype.lower():
            return "Declaration of Conformity"
        elif 'v2' in rtype.lower() or 'www' in rtype.lower() or 'firmware' in rtype.lower():
            return ""
        elif 'marc alhadeff photography' in rtype.lower():
            return "Review"
        else:
            return ''

    def clean_model(self, model):
        try:
            if 'for' in model:
                model_list = model.split('for')
                cleaned_model = model_list[0] + '(' + model_list[1] + (' )')
                cleaned_model = cleaned_model.replace('Wireless Kit ', '').replace(
                    'Pro Kit ', '').replace('Speedlight', '')
                return cleaned_model
            else:
                return model
        except (IndexError, AttributeError):
            return model

    def close(spider, reason):
        print(spider.rtypes)
