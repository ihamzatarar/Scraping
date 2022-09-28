
import scrapy


class ShokzSpider(scrapy.Spider):
    start_urls = ['https://shokz.com/', 'https://ca.shokz.com/', 'https://uk.shokz.com/',
                  'https://de.shokz.com/', 'https://www.shokz.com.cn/', 'https://fr.shokz.com/',
                  'https://www.shokz.cz/', 'https://jp.shokz.com/', 'https://shokz.co.kr/',
                  'https://nl.shokz.com/', 'https://shokz.com.vn/']
    name = 'shokz.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for url_sel in response.css('a::attr(href)').getall():
            if '/products' in url_sel or '/open' in url_sel or 'aeropex' in url_sel:
                yield response.follow(url_sel, callback=self.parse_item)

    def parse_item(self, response, **kwargs):

        # No manual check because there is variation in page structure of almost every country

        for pdf_sel in response.css('a[href*=".pdf"]'):
            manual = dict()
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)

            # Type
            rtype = self.clean_type(rfile)
            if not rtype:
                rtype = self.clean_type(pdf_sel.css("::text").get())
            if not rtype:
                rtype = self.clean_type(pdf_sel.css("span::text").get())
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype

            # Model
            model = response.css('.c-variant-picker__title::text').get()
            if not model:
                model = response.css(
                    '.product-single__meta h1::text').get()
                if response.css('.product-single__meta h1 strong::text').get():
                    model = model + ' ' + \
                        response.css(
                            '.product-single__meta h1 strong::text').get()
            if not model:
                model = response.css('title::text').get()
            if not model.strip():
                continue
            manual['model'] = model.replace(
                '- shokz', '').replace('- Shokz.cz', '').strip()

            # Product
            product = self.clean_product(model)
            manual['product'] = product

            thumb = response.css(
                'meta[property*="og:image:secure_url"]::attr(content)').get()
            if not thumb:
                continue
            manual['thumb'] = thumb
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Shokz"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'manual' in rtype.lower() or 'uživatelský manuál' in rtype.lower() or 'huong' in rtype.lower() or '日本語 >' in rtype or '-uk' in rtype.lower() or '1646184252' in rtype:
            return "User Manual"
        elif 'size' in rtype.lower():
            return "Size Guide"
        elif 'guide' in rtype.lower() or 'AEROPEX' in rtype:
            return "User Guide"
        elif 'line drawings' in rtype.lower():
            return "Line Drawings"
        elif 'instructions' in rtype.lower():
            return "Instructions"
        else:
            return ''

    def clean_product(self, model):
        if 'opencomm' in model.lower() or 'aeropex' in model.lower() or 'open comm' in model.lower():
            return 'HEADSET'
        elif 'openrun pro' in model.lower():
            return 'SPORT HEADPHONES'
        elif 'openrun' in model.lower():
            return 'ENDURANCE HEADPHONES'
        elif 'openmove' in model.lower() or 'air' in model.lower():
            return 'LIFESTYLE/SPORT HEADPHONES'
        elif 'openswim' in model.lower():
            return 'SWIMMING HEADPHONES'
        elif 'loop' in model.lower() or 'adaptateur' in model.lower():
            return 'Adapter'

    def close(spider, reason):
        print(spider.rtypes)
