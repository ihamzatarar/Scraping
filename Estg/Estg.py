import scrapy
import re

# from manual_scraper_ext.items import Manual
from scrapy.spiders import SitemapSpider


class EstgSpider(SitemapSpider):
    name = 'estg.eu'
    sitemap_urls = ['https://www.estg.eu/sitemaps/en/sitemap.xml',
                    'https://www.estg.eu/sitemaps/nl/sitemap.xml',
                    'https://www.estg.eu/sitemaps/fr/sitemap.xml',
                    'https://www.estg.eu/sitemaps/de/sitemap.xml',
                    'https://www.estg.eu/sitemaps/pl/sitemap.xml',
                    'https://www.estg.eu/sitemaps/it/sitemap.xml',
                    'https://www.estg.eu/sitemaps/hu/sitemap.xml',
                    'https://www.estg.eu/sitemaps/se/sitemap.xml',
                    'https://www.estg.eu/sitemaps/es/sitemap.xml',
                    'https://www.estg.eu/sitemaps/pt/sitemap.xml',
                    'https://www.estg.eu/sitemaps/dk/sitemap.xml',
                    'https://www.estg.eu/sitemaps/cz/sitemap.xml',
                    'https://www.estg.eu/sitemaps/fi/sitemap.xml'
                    ]
    rfiles = set()
    rtypes = set()
    custom_settings = {
        # "DOWNLOAD_DELAY": 0.3,
        # "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response, **kwargs):

        if 'nieuws' in response.url:
            return

        # pdfs = response.css('.tab-container .copy a::text').getall()
        # pdf = [pp for pp in pdfs if 'manual' in pp.lower()]
        # if not pdf:
        #     self.logger.warning("No manual found")
        #     return

        for pdf_sel in response.css('.am-filelink'):
            manual = dict()

            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.css('span::text').get())
            if not rtype:
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            model = response.css('.page-title span::text').get()
            product = response.css('.item.category a::text').get()
            brand = response.css(
                "meta[name*='keywords']::attr(content)").get()
            cleaned_model = self.clean_model(model, brand, product)
            if not cleaned_model:
                self.logger.info("No Product found")
                continue

            manual['model'] = cleaned_model
            manual['product'] = product
            manual['thumb'] = response.css(
                '.gallery-item::attr(data-srcset)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = brand.replace('Smart Plug', '')
            manual['product_lang'] = 'en'

            yield manual

    def clean_product(self, product):
        if not product:
            return product
        elif 'battery' in product.lower():
            return 'Batteries'
        else:
            return product

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'manual' in rtype.lower() or 'user_manual' in rtype.lower():
            return "Manual"
        elif 'user manual' in rtype.lower():
            return "User Manual"
        elif 'quick guide' in rtype.lower():
            return "Quick guide"
        elif 'brochure' in rtype.lower() or 'qig' in rtype.lower():
            return 'Brochure'
        elif 'datasheet' in rtype.lower():
            return "Datasheet"
        elif 'quick installation guide' in rtype.lower() or 'quick-installation-guide' in rtype.lower():
            return "Quick Installation Guide"
        elif 'installation guide' in rtype.lower() or 'installation-guide' in rtype.lower() or 'installation instructions' or rtype.lower():
            return "Installation Guide"
        elif 'service and warranty conditions' in rtype.lower():
            return "Service and warranty conditions"
        elif 'warranty' in rtype.lower():
            return "Warranty Policy"
        elif 'catalogue' in rtype.lower():
            return "Catalogue"
        elif 'compatibility list' in rtype.lower():
            return "Compatibility list"
        elif 'inventory help' in rtype.lower():
            return "Inventory help"
        elif 'technical data' in rtype.lower():
            return "Technical data"
        elif 'certificate of compliance' in rtype.lower() or 'certificate de compliance' in rtype.lower() or 'rfg' in rtype.lower():
            return "Certificate of compliance"
        elif 'service and warranty conditions' in rtype.lower():
            return "Service and warranty conditions"
        elif 'factsheet' in rtype.lower():
            return "Factsheet"
        elif 'commercial drawing' in rtype.lower():
            return "Commercial drawing"
        elif 'certificate of conformity' in rtype.lower() or 'conformity' in rtype.lower() or 'certficate' in rtype.lower() or 'ce' in rtype.lower():
            return ""
        else:
            return ''

    def clean_model(self, model, brand, product):
        if not model or not product or not brand:
            return ''
        model = re.sub("[\(\[].*?[\)\]]", "", model)
        for i in model.split():
            if brand[:2].lower() in i.lower():
                model = model.replace(i, '')
            if product[:2].lower() in i.lower():
                model = model.replace(i, '')

        extra = ['Ibrido', 'StorEdge', 'Hybrid']
        for i in extra:
            model = model.replace(i, '').strip()
        return model

    def close(spider, reason):
        print(spider.rtypes)
