import requests
import lxml.html

tab_id = "tab_newreleases_content"

html = requests.get("https://store.steampowered.com")
doc = lxml.html.fromstring(html.content)

#the syntax of the search is: expr = "//*[local-name() = $name]"
#// this two slashes means search all tag inside the doc
#/ only the image char text or node match requirement
#div[@id="tab_newreleases_content"] this means only interested at the div tab with id "tab_newreleases_content"
#'.//div[@class="tab_item_name"]/text()', "." means it only interested at its childrens tag, text() in the end to convert it to text
#get('class')
new_releases = doc.xpath('//div[@id="tab_newreleases_content"]')
title_name_tag = "tab_item_name"
price_name_tag = "discount_final_price"
tags_cols_name_tag = "tab_item_top_tags"
platform_class_name = "tab_item_details"
platfrom_name = "platform_img win"

for release in new_releases:
    titles = release.xpath('.//div[@class="{0}"]/text()'.format(title_name_tag))
    #titles = release.xpath('.//div[@class="{0}"]'.format(title_name_tag))
    #print(titles)
    prices = release.xpath('.//div[@class="{0}"]/text()'.format(price_name_tag))
    #print(prices)
    tags = release.xpath('.//div[@class="{0}"]'.format(tags_cols_name_tag))
    #print(tags)
    total_tags = []
    for tag in tags:
        total_tags.append(tag.text_content())
    #print(total_tags)

    platform_extract = release.xpath('.//div[@class="{0}"]'.format(platform_class_name))

    platforms = []
    for plat in platform_extract:
        temp = plat.xpath('.//span[contains(@class, "platform_img")]')
        #print(temp)
        plat_form_sub_list = []
        for t in temp:
            class_temp = t.get('class').split()[-1]
            #print("class_temp", class_temp)
            plat_form_sub_list.append(class_temp)
        platforms.append(plat_form_sub_list)

    #print(platforms)

    output = []
    for info in zip(titles, prices, total_tags, platforms):
        title, price,tag,platform = info
        #print(info)
        resp = {}
        resp["title"] = title
        resp["price"] = price
        resp["tag"] = tag
        resp["platform"] = platform
        output.append(resp)

    print(output)



