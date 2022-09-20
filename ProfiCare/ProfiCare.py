import scrapy
from scrapy.spiders import SitemapSpider
# class Spider(SitemapSpider):
#


class ProfiCareSpider(SitemapSpider):
    sitemap_urls = [
        'https://www.proficare-germany.de/sitemaps/sitemap_proficare_en.xml', ' https://www.proficare-germany.de/sitemaps/sitemap_proficare_de.xml', ]
#     sitemap_rules = [('', 'parse')]
    name = 'proficare-germany.de'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response, **kwargs):

        pdfs = response.css(
            "a[href*='.pdf']").xpath('./../preceding-sibling::td[1]/text()').getall()
        pdf = [pp for pp in pdfs if 'operating instructions' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*=".pdf"]'):
            if 'www.clatronic.de' in response.url:
                continue
            manual = dict()
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.xpath('./../preceding-sibling::td[1]/text()').get()
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            title = response.css('.page-title span::text').get()
            cleaned_title = self.clean_title(title)
            if not cleaned_title:
                continue
            manual['product'] = cleaned_title[1]
            if not cleaned_title[1]:
                continue
            manual['eans'] = response.css(
                'div[itemprop*="ean_code"]::text').get()
            manual['thumb'] = response.css(
                '.img-responsive.border.m-2::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "ProfiCare"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]
            model = cleaned_title[0]
            if not model:
                continue

            if isinstance(model, list):
                manual['model'] = model[0]
                yield manual
                model = model[1]
            manual['model'] = model
            yield manual

    def clean_title(self, title):
        if not title:
            return title
        title_list = title.split()
        model = ''
        try:
            for i, a in enumerate(title_list):
                if '-' in a:
                    model = a + ' ' + title_list[i+1]
            if not model:
                return model
            product = title.replace('ProfiCare ', '').split(model)[0]
            if '/' in model:
                no = model.split()[1]
                model_1 = model.split('/')[0] + ' ' + no
                model_2 = 'PC-' + model.split('/')[1]
                model = [model_1, model_2]

            return model, product
        except (IndexError, ValueError):
            return ''

    def close(spider, reason):
        print(spider.rtypes)
