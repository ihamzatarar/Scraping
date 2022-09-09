import scrapy


class OptexEuropeSpider(scrapy.Spider):
    name = 'optex-europe.com'
    start_urls = ['https://www.optex-europe.com/', 'https://www.optex-europe.com/pl', 'https://www.optex-europe.com/nl',
                  'https://www.optex-europe.com/it', 'https://www.optex-europe.com/es/', 'https://www.optex-europe.com/fr',
                  'https://www.optex-europe.com/de/']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for categ_sel in response.css('.nav-children a::attr(href)').getall():
            url = response.urljoin(categ_sel)
            yield response.follow(url, callback=self.parse_prod)

    def parse_prod(self, response):
        for prod_url in response.css('.product-image').xpath('./..').css('::attr(href)').getall():
            yield response.follow(prod_url, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        pdfs = response.css('#downloads a[href*=".pdf"]::text').getall()
        pdf = [pp for pp in pdfs if self.clean_type(pp.strip()) == 'Manual']
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('#downloads a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = self.clean_type(pdf_sel.css('::text').get().strip())
            if not rtype:
                continue
            self.rtypes.add(rtype)
            breadcrumb = response.css('.breadcrumb a::text').getall()
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            model = response.css('h1::text').get()
            manual['model'] = self.clean_model(model)
            manual['product'] = breadcrumb[1]
            manual['thumb'] = response.css(
                '.product-image img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "optex-europe.com"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif rtype == 'Podłączenie 3 EOL 2 EOL':
            return ''
        elif 'datasheet' in rtype.lower() or 'vxi' in rtype.lower() or 'doc' in rtype.lower() or 'viik' in rtype.lower() or 'wxi' in rtype.lower() or 'series' in rtype.lower() or 'Podłączenie' in rtype.lower():
            return "Datasheet"
        elif 'declaration-of-conformity' in rtype.lower() or 'declaration of conformity' in rtype.lower():
            return ""
        elif 'manual' in rtype.lower() or 'instrukcja obsługi' in rtype.lower() or 'instrukcja obslugi' in rtype.lower() or 'skrocony podrecznik' in rtype.lower():
            return "Manual"
        elif 'quick reference guide' in rtype.lower() or 'quick-reference-guide' in rtype.lower():
            return "Quick reference guide"
        elif 'technicalguide' in rtype.lower():
            return "Technical guide"
        elif 'techniqueguide' in rtype.lower():
            return 'Technique Guide'
        elif 'brochure' in rtype.lower():
            return "Brochure"
        elif 'leaflet' in rtype.lower():
            return "Leaflet"
        elif 'app guide' in rtype.lower():
            return "App Guide"
        elif '_assembly_instr' in rtype.lower():
            return "Assembly Instructions"
        elif 'catalogue' in rtype.lower() or 'katalog' in rtype.lower():
            return "Catalogue"
        elif 'instrukcja' in rtype.lower():
            return "Instructions"

        else:
            return rtype

    def clean_model(self, model):
        a = ''
        remove = ['Zewnętrzna czujka dualna PIR', 'Szerokokątna, zewnętrzna czujka dualna PIR', 'Zewnętrzna, bezprzewodowa czujka dualna PIR', 'Zewnętrzna czujka dualna PIR',
                  'Szerokokątna, zewnętrzna czujka dualna PIR', 'PIR', 'LiDAR', 'IR', 'REDWALL', 'Redwall', 'Kit', 'Outdoor']
        if '/' in model:
            clean_model = model.split('/')[0]
            for i in remove:
                clean_model = clean_model.replace(i, '').strip(',').strip()
            return clean_model
        s = model.split()
        if len(s) == 1:
            return model
        for i in s:
            if len(i) > 1 and i[:2].isupper():
                a += ' ' + i
            elif i.isupper():
                a += ' ' + i

        clean_model = a
        for i in remove:
            clean_model = clean_model.replace(i, '').strip(',').strip()
        return clean_model

    def close(spider, reason):
        print(spider.rtypes)
