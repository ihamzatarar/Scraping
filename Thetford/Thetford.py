
import scrapy
import re
import json
from scrapy.spiders import SitemapSpider


class ThetfordSpider(SitemapSpider):
    sitemap_urls = ['https://www.thetford-europe.com/sitemap.xml']
    sitemap_rules = [('/products/', 'parse')]
    name = 'thetford-europe.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response, **kwargs):

        try:
            script = response.css('script').getall()[-1]
            data = re.search(r'var p =(.*\s)', script).group(1)
            data_obj = json.loads(data)
        except AttributeError:
            self.logger.warning("No pdf found")
            return

        pdfs = ''
        for i in data_obj["blocks"]:
            if i["kind"] == 'F13':
                pdfs = i["value"]["support"]["documents"]

        if 'User manual' in pdfs:
            for type in pdfs:
                for pdf in pdfs[type]:
                    manual = dict()
                    rfile = pdf["url"]
                    if rfile in self.rfiles:
                        continue
                    self.rfiles.add(rfile)
                    rtype = type
                    self.rtypes.add(rtype)
                    product_info = ''
                    for i in data_obj["blocks"]:
                        if i["kind"] == 'F4':
                            product_info = i["value"]
                    manual['file_urls'] = [rfile]
                    manual['type'] = rtype
                    manual['product'] = product_info['subcategory']
                    thumb = product_info["imageSizes"][0]["Sizes"]["878x878"]
                    manual['thumb'] = thumb
                    manual['url'] = response.url
                    manual['source'] = self.name
                    manual['brand'] = "Thetford"
                    manual['product_lang'] = response.css(
                        'html::attr(lang)').get().split('-')[0]

                    model = self.clean_model(product_info['name'])
                    if not model:
                        continue
                    if isinstance(model, list):
                        for i in model:
                            manual['model'] = i
                            yield manual
                    else:
                        manual['model'] = model
                        yield manual
        else:
            self.logger.warning("No manual found")
            return

    def clean_model(self, model):
        if not model:
            return model
        if '-' in model:
            model = model.split('-')
            if model[1].isupper():
                model = model[0]+'-'+model[1]
            else:
                model = model[0]
        if '(' in model:
            model = re.sub("[\(\[].*?[\)\]]", "", model)
        if '/' in model:
            model = model.split('/')
        return model

    def close(spider, reason):
        print(spider.rtypes)
