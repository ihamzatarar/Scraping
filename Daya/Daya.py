import scrapy
from scrapy.spiders import SitemapSpider


class DayaSpider(SitemapSpider):
    sitemap_urls = ['https://dayahome.it/product-sitemap.xml']
    name = 'dayahome.it'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response, **kwargs):

        pdfs = []
        for pd in response.css(".elementor-button-link.elementor-button.elementor-size-xs"):
            pdfs.append(pd.css("span::text").getall()[-2])
        pdf = [pp for pp in pdfs if 'manuale utente' in pp.lower()]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('.elementor-button-link.elementor-button.elementor-size-xs'):
            manual = dict()
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.css("span::text").getall()[-2]
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            manual['model'] = response.css(
                '.product_title.entry-title.elementor-heading-title.elementor-size-default::text').get()
            try:
                manual['product'] = response.css(
                    '.woocommerce-breadcrumb a::text').getall()[1]
            except IndexError:
                if 'Congelatore' in response.css('.elementor-text-editor.elementor-clearfix p::text').get():
                    manual['product'] = 'Congelatori'
                else:
                    self.logger.info("No Product found")
                    continue
            thumb = response.css(
                '.jet-woo-product-gallery__image-link::attr(href)').get()
            if not thumb:
                self.logger.info("No Thumb found")
                continue
            manual['thumb'] = thumb
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "DAYA"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual
