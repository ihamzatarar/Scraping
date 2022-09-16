from turtle import rt
import scrapy


class GenelecSpider(scrapy.Spider):
    name = 'genelec.com'
    start_urls = ['https://www.genelec.com/']
    rfiles = set()
    rtypes = set()
    custom_settings = {
        'CONCURRENT_REQUESTS': 5,
        "DOWNLOAD_DELAY": 2,
    }

    def parse(self, response):
        for url in response.css('.nav-flex-container a::attr(href)').getall():
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        pdfs = response.css("a[href*='.pdf'] span::text").getall()
        pdf = [pp for pp in pdfs if 'operating manual' in pp.lower()
               or 'user guide' in pp.lower()]
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
            breadcrumb = response.css('.breadcrumb-item span::text').getall()
            try:
                manual['model'] = breadcrumb[-1].replace(
                    'IP', '').replace('Smart', '')
                manual['product'] = breadcrumb[-2]
                manual['product_parent'] = breadcrumb[-3]
            except IndexError:
                self.logger.info("breadcrumb Not Found")
                continue
            manual['thumb'] = response.urljoin(response.css(
                '.image-carousel-wrapper a::attr(href)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Genelec"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'operating manual' in rtype.lower() or '用户操作手册' in rtype:
            return "Operating Manual"
        elif 'installation manual' in rtype.lower():
            return "Installation Manual"
        elif 'datasheet' in rtype.lower():
            return "Datasheet"
        elif 'catalogue' in rtype.lower():
            return "Catalogue"
        elif 'instructions' in rtype.lower():
            return "Instructions"
        elif 'setup guide' in rtype.lower():
            return 'Quick Setup Guide'
        elif 'channel management' in rtype.lower():
            return 'Application Note'
        elif 'simulation file' in rtype.lower():
            return "Simulation File"
        elif 'magazine' in rtype.lower():
            return "Magazine"
        elif 'user guide' in rtype.lower():
            return "User Guide"
        elif 'waveguides' in rtype.lower():
            return "Waveguides"
        elif 'line drawing' in rtype.lower():
            return "Line Drawings"
        elif 'faq' in rtype.lower():
            return "FAQ"
        elif 'case study' in rtype.lower():
            return "Case Study"
        elif 'brochure' in rtype.lower() or '- chinese' in rtype.lower() or '产品手册' in rtype or '智能监听音箱 (中文)' in rtype:
            return "Brochure"
        else:
            return rtype

    def close(spider, reason):
        print(spider.rtypes)
