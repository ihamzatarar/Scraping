#from manual_scraper_ext.items import Manual

import scrapy
from scrapy.spiders import SitemapSpider
import re


class FisherPaykelSpider(SitemapSpider):
    name = 'fisherpaykel.com'
    sitemap_urls = ['https://www.fisherpaykel.com/us/sitemap_index.xml',
                    'https://www.fisherpaykel.com/ca/sitemap_index.xml',
                    'https://www.fisherpaykel.com/au/sitemap_index.xml',
                    'https://www.fisherpaykel.com/uk/sitemap_index.xml',
                    'https://www.fisherpaykel.com/sg/sitemap_index.xml',
                    'https://www.fisherpaykel.com/nz/sitemap_index.xml']

    sitemap_rules = [('/cooling/', 'parse'), ('/cooking/', 'parse'),
                     ('/laundry/', 'parse'), ('/accessories/', 'parse'),
                     ('/dishwashing/', 'parse'), ('/ventilation/', 'parse'),
                     ('/outdoor/', 'parse'), ('/cooker-hoods/', 'parse')]
    rfiles = set()
    rtypes = set()

    def parse(self, response, **kwargs):

        # Check for manual
        manuals = ['User and Installation Guide', 'user', 'Spec Guide', '\nQuick Reference guide' 'Guide D’Installation', 'User Install Guide',
                   'DataSheet Chest Freezer with 30inch Trim', 'Guide D’Utilisation', 'Wash Program Data Sheet', 'Planning Guide - PDF',
                   'Quick Start Guide FR', 'Specification Guide', 'Cavity Sizes Guide', 'User Guide FR', 'Pairing Guide', 'Specification Guide - PDF',
                   'Quick Start Guide', 'Planning Guide', 'Datasheet', 'installation', 'User & Installation Guide - Professional Grill Cart',
                   'Alternate Install Guide', 'User Install', 'User Guide', 'Data Sheet', 'Data Sheet - PDF', 'Install Guide FR', 'Installation Guide', 'Install Guide', 'Quick Reference guide']

        pdfs = []
        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            try:
                rtype = self.clean_type(str(rfile))
            except AttributeError:
                rtype = pdf_sel.xpath(
                    'following-sibling::label[1]/span/text()').get()
            pdfs.append(rtype)
        pdf = [pp for pp in pdfs if pp in manuals]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            manual = dict()
            rfile = pdf_sel.css("::attr(href)").get()
            if 'https:' not in rfile:
                rfile = response.urljoin(rfile)
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            try:
                rtype = self.clean_type(str(rfile))
            except AttributeError:
                rtype = pdf_sel.xpath(
                    'following-sibling::label[1]/span/text()').get()
            self.rtypes.add(rtype)
            if not rtype:
                self.logger.info('Type Not Found')
                continue
            manual['file_urls'] = [rfile]
            manual['type'] = rtype.strip()
            manual['model'] = response.css('.model-number span::text').get()
            try:
                manual['product'] = response.css(
                    '.breadcrumb-item a::text').getall()[-1].strip()
            except IndexError:
                self.logger.info('Product Not Found')
                continue
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Fisher & Paykel"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        b = re.search(r'FP-(\w*)-', rtype).group(1)
        return re.sub(r"(\w)([A-Z])", r"\1 \2", b)

    def close(spider, reason):
        print(spider.rtypes)
