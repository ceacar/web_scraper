from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import json
import time
import excalibur
import os
import pathlib


log = excalibur.logger.getlogger()


class NetLoopScrapper:
    PRICE_FIELD_NAME = 'Price'
    HISTORICAL_PRICE_FIELD_NAME = 'historical_prices'
    INFO_FIELD_NAME = 'info'

    def __init__(self, email_list):
        self.email_cache = []
        self.price_changed = False
        self.email_list = email_list
        pass

    def soupify(self, url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        # Creating a BeautifulSoup object of the html page for easy extraction of data.
        soup = BeautifulSoup(webpage, 'html.parser')
        return soup

    def strip_text(self, bs4element):
        return bs4element.text.replace('\r\n', '').strip()

    def parse_table(self, tbl_soup_obj) -> list:
        table_dict_list = []
        for soup_temp in tbl_soup_obj:
            try:
                table_dict = {}
                columns_soup = soup_temp.find_all('td')
                k1, v1, k2, v2 = columns_soup
                table_dict[self.strip_text(k1)] = self.strip_text(v1)
                table_dict[self.strip_text(k2)] = self.strip_text(v2)
                table_dict_list.append(table_dict)
            except Exception:
                pass

        return table_dict_list

    def scrap_detail(self, url):
        """
        exmaple json return
        {'address': '2510 38th Ave, New York, Long Island City',
         'category': 'Multifamily',
         'info': {'Apartment Style': 'Mid Rise',
         'Average Occupancy': '100%',
         'Building Class': 'A',
         'Building Size': '22,369 SF',
         'Cap Rate': '5.25%',
         'Lot Size': '0.09 AC',
         'No. Stories': '8',
         'No. Units': '19',
         'Parking Ratio': '0.54/1,000 SF',
         'Price': 'Upon Request',
         'Property Sub-type': 'Apartments',
         'Property Type': 'Multifamily',
         'Sale Type': 'Investment',
         'Year Built': '2018'},
         'name': '2510 38th Ave - Newly Built 19 Unit Multi Family',
         'timestamp': '2020-03-15 23:10:04',
         'url': 'https://www.loopnet.com/Listing/2510-38th-Ave-Long-Island-City-NY/15870702/'}
        """
        soup = self.soupify(url)
        tbl_json_soup = soup.findAll('table', attrs={'class': 'property-data featured-grid'})

        table_results = []
        for tbl_soup in tbl_json_soup:
            parsed_dict = self.parse_table(tbl_soup)
            table_results.append(parsed_dict)

        property_detail = {}
        property_detail[self.INFO_FIELD_NAME] = excalibur.misc.flat_dict_list(table_results)

        ld_json_soup = soup.findAll('script', attrs={'type': 'application/ld+json'})

        for s in ld_json_soup:
            try:
                j_temp = json.loads(s.text)
                about = excalibur.json_utility.get_json_value_by_key(j_temp, 'about', {})
                property_detail['category'] = excalibur.json_utility.get_json_value_by_key(about, 'category')
                property_detail['name'] = excalibur.json_utility.get_json_value_by_key(about, 'name')
                property_detail['url'] = excalibur.json_utility.get_json_value_by_key(about, 'url')
                address_form = excalibur.json_utility.get_json_value_by_key(about, 'availableAtOrFrom', {})
                address = excalibur.json_utility.get_json_value_by_key(address_form, 'address', {})
                st_address = excalibur.json_utility.get_json_value_by_key(address, 'streetAddress')
                state = excalibur.json_utility.get_json_value_by_key(address, 'addressRegion')
                city = excalibur.json_utility.get_json_value_by_key(address, 'addressLocality')
                property_detail['address'] = ', '.join([st_address, state, city])

            except Exception:
                log.warning("Failed to retrieve detail for {}".format(url))

        # timestamp this property
        property_detail['timestamp'] = excalibur.time_conversion.get_current_date()
        property_detail[self.HISTORICAL_PRICE_FIELD_NAME] = {}
        return property_detail

    def get_file_name_from_address(self, listing_detail):
        address_string = listing_detail['address']
        name = listing_detail['name']
        file_name = address_string + '___' + name
        return file_name.replace(' ', '_').replace(',', '-').replace('|', '-').replace('/', '-')

    def get_file_relative_path(self, json_obj):
        file_name = self.get_file_name_from_address(json_obj)
        return './scrap_cache/{file_name}.json'.format(file_name=file_name.lower())

    def write_to_file(self, json_obj):
        with open(self.get_file_relative_path(json_obj), 'w') as f:
            f.write(json.dumps(json_obj))

    def create_path_if_not_exists(self):
        pathlib.Path("./scrap_cache").mkdir(parents=True, exist_ok=True)

    def merge_historical_prices(self, new_json, old_json):
        # merges historical price with old, if old json doesn't have it , then we will take current newprice and old price as the list
        if self.HISTORICAL_PRICE_FIELD_NAME in old_json:
            new_json[self.HISTORICAL_PRICE_FIELD_NAME] = old_json[self.HISTORICAL_PRICE_FIELD_NAME]
        else:
            new_json[self.HISTORICAL_PRICE_FIELD_NAME] = []

        new_json[self.HISTORICAL_PRICE_FIELD_NAME].append(self.get_price_from_listing_detail(new_json))

        return new_json

    def get_old_listing_detail(self, json_scrap_detail):
        self.create_path_if_not_exists()
        cache_file_path = self.get_file_relative_path(json_scrap_detail)

        if not os.path.exists(cache_file_path):
            return {}

        with open(cache_file_path, 'r') as f:
            lines = f.readlines()
            json_str = ''.join(lines)
            json_old = json.loads(json_str)
            return json_old

    def get_price_from_listing_detail(self, listing_detail: dict) -> str:
        info = excalibur.json_utility.get_json_value_by_key(listing_detail, self.INFO_FIELD_NAME, {})
        return excalibur.json_utility.get_json_value_by_key(info, self.PRICE_FIELD_NAME, "")

    def has_price_changed(self, json_scrap_detail, json_old) -> (bool, str, str):
        price_new = self.get_price_from_listing_detail(json_scrap_detail)
        if not json_old:
            return True

        price_old = self.get_price_from_listing_detail(json_old)
        if price_old == price_new:
            return False
        else:
            # we want to printout log to trouble shoot why price fluctuates a lot
            log.info("price has changed from \n{} to \n{}".format(price_old, price_new))
            return True

    def write_to_file_if_updated(self, json_scrap_detail):
        old_listing_detail = self.get_old_listing_detail(json_scrap_detail)
        has_price_changed = self.has_price_changed(json_scrap_detail, old_listing_detail)
        if has_price_changed:
            # flip on the flag on change have taken place, so email can send out
            self.price_changed = True
            merged_listing_detail = self.merge_historical_prices(json_scrap_detail, old_listing_detail)
            self.cache_changes_for_email(merged_listing_detail, old_listing_detail)
            self.write_to_file(merged_listing_detail)
        else:
            log.info('Price unchanged, skipped')

    def cache_changes_for_email(self, new_listing_detail: dict, old_listing_detail: dict) -> None:
        address, old_price = new_listing_detail['address'], self.get_price_from_listing_detail(old_listing_detail),
        new_price, url, historical_prices = self.get_price_from_listing_detail(new_listing_detail), new_listing_detail["url"], new_listing_detail[self.HISTORICAL_PRICE_FIELD_NAME]
        self.email_cache.append("地址:{address} 价格从 {o} 变更至 {n}, 网址:{url}, 历史价格:{historical_prices} ".format(
            address=address,
            o=old_price,
            n=new_price,
            url=url,
            historical_prices='->'.join(historical_prices)))

    def email_if_updated(self):
        if self.price_changed:
            for receiver in self.email_list:
                log.info(f"Emailing {receiver}")
                excalibur.email_utility.send_email(
                    username='',
                    password="",
                    subject="NetLoop 价格变动",
                    date=excalibur.time_conversion.get_current_date(),
                    message_text="\n".join(self.email_cache),
                    to=receiver,
                )

    def run(self, area_string):
        url = self.formulate_url(area_string)
        log.info("Analyzing {}".format(url))
        soup = self.soupify(url)

        ld_json_soup = soup.findAll('script', attrs={'type': 'application/ld+json'})

        for script in ld_json_soup:

            json_obj = json.loads(script.text.replace(",}", "}"))
            for about in json_obj['about']:
                detail_url = about['item']['url']
                log.info("Scrapping {}".format(detail_url))
                json_scrap_detail = self.scrap_detail(detail_url)
                self.write_to_file_if_updated(json_scrap_detail)
                time.sleep(1.5)
        self.email_if_updated()

    def formulate_url(self, area_string):
        return "https://www.loopnet.com/search/commercial-real-estate/{area_code}/for-sale".format(area_code=area_string)


def monitor_loopnet(area_netloop_code, email_list):
    for area_string in area_netloop_code:
        NetLoopScrapper(email_list=email_list).run(area_string)
