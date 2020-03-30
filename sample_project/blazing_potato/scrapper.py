import requests
import lxml.html
import misc

class Scrapper:
    def __init__(self):
        pass

    def scrap(self, url:str, ids:[dict]) -> dict:
        """
        "url":"https://www.amazon.com/Seagate-ST1000NM0033-Enterprise-Storage-7200RPM/dp/B00BVW6MEO"
        "ids":[{"identifier":"span", "id":"blahblah"}]
        """
        website_str = requests.get(url)
        doc = lxml.html.fromstring(website_str.content)

        res = {}

        for the_id in ids:
            if "id" not in the_id or "identifier" not in the_id:
                #wrong format
                return []
            id = the_id["id"]
            identifier = the_id["identifier"]

            ins_unsanitized = doc.xpath(
                '//{identifier}[@id="{id}"]/text()'.format(
                    identifier = identifier, id = id)
            )
            sanitized_list = misc.sanitize_string_list(ins_unsanitized)
            res[id] = sanitized_list
        print("scrap result", res)
        return res
        #support amazon for now
        #website_str = requests.get(url)
        #doc = lxml.html.fromstring(website_str.content)
        #title_id = "productTitle"
        #title_unsanitized = doc.xpath('//span[@id="{0}"]/text()'.format(title_id))
        #title_sanitized = misc.unformat_str_list(title_unsanitized)

        #price_id = "priceblock_ourprice"
        #price_unsanitized = doc.xpath('//span[@id="{0}"]/text()'.format(price_id))
        #price_sanitized = misc.unformat_str_list(price_unsanitized)

        #res = {}
        #res["title"] = title_sanitized
        #res["price"] = price_sanitized

        #return res














__scrapper_ins = None

def get_scrapper():
    #singleton
    global __scrapper_ins
    if not __scrapper_ins:
        __scrapper_ins = Scrapper()
    return __scrapper_ins

