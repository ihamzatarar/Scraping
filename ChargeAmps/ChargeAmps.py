
import scrapy


class ChargeAmpsSpider(scrapy.Spider):
    start_urls = ['https://chargeamps.com/support/',
                  'https://chargeamps.com/da/support/',
                  'https://chargeamps.com/sv/support/',
                  'https://chargeamps.com/pt/apoio-ao-cliente/',
                  'https://chargeamps.com/fi/tuki/',
                  'https://chargeamps.com/es/servicio-posventa/',
                  'https://chargeamps.com/no/brukerstotte/',
                  'https://chargeamps.com/nl/support/',
                  'https://chargeamps.com/fr/service-apres-vente/',
                  'https://chargeamps.com/de/support/', ]
    name = 'chargeamps.com'
    rfiles = set()
    rtypes = set()
    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response, **kwargs):

        check = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
            title = pdf_sel.css('span::text').get()
            type = self.clean_type(title)
            model = self.clean_model(title)
            if model not in check:
                check[model] = [type]
            else:
                check[model] += [type]

        for pdf_sel in response.css('a[href*=".pdf"]'):
            manual = dict()
            title = pdf_sel.css('span::text').get()
            model = self.clean_model(title)

            if "User Manual" in check[model]:
                rfile = pdf_sel.css("::attr(href)").get()
                if rfile in self.rfiles:
                    continue
                self.rfiles.add(rfile)
                rtype = self.clean_type(title)
                if not rtype:
                    continue
                self.rtypes.add(rtype)
                manual['file_urls'] = [rfile]
                manual['type'] = rtype
                manual['model'] = model
                manual['product'] = 'No Cateogy'
                manual['url'] = response.url
                manual['source'] = self.name
                manual['brand'] = "Charge Amps"
                manual['product_lang'] = response.css(
                    'html::attr(lang)').get().split('-')[0]

                yield manual
            else:
                self.logger.warning("No manual found")
                continue

    def clean_type(self, rtype):
        if not rtype:
            return rtype
        elif 'user manual' in rtype.lower() or 'brugervejledning' in rtype.lower() or 'gebrauchsanleitung' in rtype.lower() or "mode d'emploi " in rtype.lower() or 'bruksanvisning' in rtype.lower() or 'brugermanual' in rtype.lower() or 'användarmanual' in rtype.lower() or 'manual de usuario' in rtype.lower() or 'käyttöohje' in rtype.lower() or 'brukermanual' in rtype.lower() or 'handleiding' in rtype.lower() or 'gebruikershandleiding' in rtype.lower():
            return "User Manual"
        elif 'installation manual' in rtype.lower() or 'installationsvejledning' in rtype.lower() or 'installationsmanual' in rtype.lower() or 'manual de instalación' in rtype.lower() or 'installationshandbuch' in rtype.lower() or "manuel d’installation" in rtype.lower() or 'manual de utilização' in rtype.lower() or 'manual de instalação' in rtype.lower() or 'installatiehandleiding' in rtype.lower() or 'installasjonshåndbok' in rtype.lower() or 'latausaseman asennusohje' in rtype.lower():
            return "Installation Manual"
        elif 'datasheet' in rtype.lower() or 'ficha de produto' in rtype.lower() or 'fiche produit' in rtype.lower() or 'produktblad' in rtype.lower() or 'ficha de producto' in rtype.lower() or 'produktblatt' in rtype.lower() or 'productblad' in rtype.lower():
            return "Data Sheet"
        elif 'quick guide' in rtype.lower():
            return "Quick Guide"
        elif 'brochure' in rtype.lower() or 'broschyr' in rtype.lower() or 'folleto de' in rtype.lower() or 'esite' in rtype.lower() or 'broschüre' in rtype.lower() or 'brochura' in rtype.lower():
            return ""
        else:
            return rtype

    def clean_model(self, model):
        if not model:
            return model
        model = model.split('-')[0].replace('Charge Amps', '')
        rtype = ['Brochure', 'Quick Guide', 'Installation Manual', 'Datasheet', 'User Manual', 'Brugervejledning', 'Brugermanual  ', 'Brukermanual  ',
                 "Mode d'emploi ", 'Fiche produit  ', 'Gebrauchsanleitung  ', 'Productblad ', 'Bruksanvisning', 'Installasjonshåndbok', 'Handleiding',
                 'Manual de utilização', 'Manual de instalação ', 'Ficha de produto ', 'Användarmanual  ', 'Installationsmanual  ',
                 'Produktblad', 'Installatiehandleiding', 'Brochura', 'Manual de instalación', 'Manual de usuario', 'Installationsvejledning',
                 'Ficha de producto', 'Installationshandbuch', 'Produktblatt', 'Manuel d’installation', 'Gebruikershandleiding', 'Product', '— versão em cinzento']
        for i in rtype:
            model = model.replace(i, '')
        if 'Seriennummer' in model:
            model = model.split('-')[0]
        model = model.strip()
        return model

    def close(spider, reason):
        print(spider.rtypes)
