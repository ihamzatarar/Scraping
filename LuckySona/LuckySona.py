import re
from scrapy.spiders import SitemapSpider


class LuckySonarSpider(SitemapSpider):
    name = 'luckysonar.com'
    sitemap_urls = ['https://www.luckysonar.com/sitemap_index.xml']
    sitemap_rules = [('/product/', 'parse')]
    rfiles = set()
    rtypes = set()

    def parse(self, response, **kwargs):
        manual = dict()

        pdfs = response.css(
            "a[href*='.pdf']").xpath('./../..').css('h6::text').getall()
        pdf = [pp for pp in pdfs if 'manual' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.xpath(
                './../..').css('h6::text').get())
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            breadcrumb = response.css('.g-breadcrumbs-item a::text').getall()
            manual['model'] = self.clean_model(response.css('h1::text').get())
            manual['product'] = "Fish finder"
            manual['thumb'] = response.css(
                '.woocommerce-product-gallery__image a::attr(href)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Lucky"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'manual' in rtype.lower():
            return "Manual"
        else:
            return rtype

    def clean_model(self, model):
        if "(" in model:
            return re.sub("[\(\[].*?[\)\]]", "", model)
        else:
            return model

    def close(spider, reason):
        print(spider.rtypes)
