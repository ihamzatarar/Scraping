import re

import scrapy

from manual_scraper_ext.items import Manual
from manual_scraper_ext.utils.text_optimization import is_word_alphanumeric


class BartscherComSpider(scrapy.Spider):
    name = 'bartscher.com'

    custom_settings = {
        "CONCURRENT_REQUESTS": 6,
        "DOWNLOAD_DELAY": 0.3,
    }

    start_urls = [
        "https://www.bartscher.com/en",
    ]

    def parse(self, response, **kwargs):
        cat_urls = response.css(
            '.nav-categories-list-sub-item-link::attr(href)').getall()
        for url in cat_urls:
            yield response.follow(url, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_url in response.css(".product-item .thumb::Attr(href)").getall():
            yield response.follow(prod_url, callback=self.parse_item)

        if next := response.css(".pagination-next a::attr(href)").get():
            yield response.follow(next, callback=self.parse_listing)

    def parse_item(self, response, **kwargs):

        pdfs = response.css(".tabhead").xpath(
            "./a[contains(text(), 'Downloads')]/../following-sibling::div[1]//a/text()").getall()
        pdf = [pp for pp in pdfs if 'operating instructions' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        name_s = '#p-name::text, .breadcrumb .active::text'
        model = response.css(name_s).get()
        if not model:
            return

        optimized_model = self.optimize_model(model.strip())
        for pdfs_div in response.css(".tabhead").xpath(
                "./a[contains(text(), 'Downloads')]/../following-sibling::div[1]//a"):
            manual = Manual()
            manual['file_urls'] = [response.urljoin(
                pdfs_div.css('::attr(href)').get())]
            manual['type'] = self.clean_type(
                pdfs_div.css('::text').get()).title()
            manual['brand'] = 'Bartscher'
            manual['source'] = self.name
            manual['url'] = response.url
            manual['product_lang'] = response.css(
                "html::attr(lang)").get().split("-")[0]
            if thumb := response.css(".gallery-image.js-gallery-image img::attr(data-zoom-image)").get():
                manual['thumb'] = response.urljoin(thumb)

            manual['model'] = optimized_model
            manual['model_2'] = response.css(".code::text").get()
            try:
                manual['product'] = response.css(
                    ".breadcrumb a::text").getall()[-1]
            except IndexError:
                self.logger.warning("Product not found")
                return

            yield manual

    def clean_type(self, raw_type):
        type = re.sub(r"\s-.*", "", raw_type)
        type = re.sub(r"\(.*\)", "", type)
        type = re.sub(r"\[.*\]", "", type)

        return type.strip()

    @staticmethod
    def optimize_model(model):
        dim_exps = (
            r'\d+x\d+.*?,'
            r'\d[\.,]?\dL.*|\d+x\d+.*',
            r'((?:\d x )?\d\/\d.*?)\,',
            r'\d+,.*',
            r'(?:\d x )?\d\/\d.*',
        )
        for dim_exp in dim_exps:
            if dim_model := re.findall(dim_exp, model):
                return dim_model[0]

        def join_l(l): return ' '.join(l)
        m_split = model.split()
        for m_elem in m_split:
            m_idx = m_split.index(m_elem)
            if is_word_alphanumeric(m_elem):
                try:
                    prev_elem = m_split[m_idx-1]
                    if prev_elem.isupper() or prev_elem.isdigit():
                        return join_l(m_split[m_idx-1:])
                    return join_l(m_split[m_idx:])
                except:
                    return join_l(m_split[m_idx:])

        return model
