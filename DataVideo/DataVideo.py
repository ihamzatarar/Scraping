
import scrapy


class DataVideoSpider(scrapy.Spider):
    name = 'datavideo.com'
    start_urls = ['https://www.datavideo.com/categories']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for lang_sel in response.css('.col-xl-3.col-lg-4.col-sm-6.col-12.mb-3 a::attr(href)').getall():
            yield response.follow(response.urljoin(lang_sel), callback=self.parse_categ)

    def parse_categ(self, response):
        for cat_sel in response.css(".col-md-6.col-lg-4.mb-4 a::attr(href)").getall():
            url = response.urljoin(cat_sel)
            yield response.follow(url, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_url in response.css(".c-product-card-hover::attr(href)").getall():
            yield response.follow(response.urljoin(prod_url), callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        pdfs = response.css("a[href*='download']").xpath(
            './../../../preceding-sibling::div[1]').css('h4::text').getall()
        pdf = [pp for pp in pdfs if pp != '' and pp.lower().strip()
               == 'manual']
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('a[href*="download"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.xpath(
                './../../../preceding-sibling::div[1]').css('h4::text').get())
            if not rtype:
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype
            breadcrumb = response.css('.breadcrumb-item a::text').getall()
            try:
                manual['model'] = response.css('.mb-3::text').get().strip()
                product = breadcrumb[-1].strip().strip('\n')
                if not product:
                    continue
                manual['product'] = product
            except(AttributeError, IndexError):
                self.logger.info("Product not found")
                continue
            thumb = response.css(
                '.swiper-slide.swiper-slide--image a::attr(href)').get()
            if not thumb:
                thumb = response.css('.img-fluid.c-image::attr(src)').get()
            manual['thumb'] = thumb
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Datavideo"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif rtype.strip() == 'Software' or rtype.strip() == 'Firmware':
            return ""
        elif rtype.strip() == 'Manual':
            return "Instruction manual"
        else:
            return rtype.strip()
