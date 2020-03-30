import pprint
import os
import json
import pandas as pd
import sys
import sdgo_proxy

# search_result_path = os.path.expanduser('~/temp/zillow/search_result1.txt')

path = sys.argv[1]

search_result_path = os.path.expanduser(path)
json_obj = None
with open(search_result_path, 'r') as f:
    json_obj = json.load(f)


search_results = json_obj['searchResults']
map_results = search_results['mapResults']
print("total {} records".format(len(map_results)))

# condo = [m['hdpData']['homeInfo']['homeType'] for m in map_results if 'hdpData' in m]
home_info_list = [m['hdpData']['homeInfo'] for m in map_results if 'hdpData' in m]

building_info_list = filter(lambda x: 'buildingId' in x, map_results)

# home_info example:
# [
#     {'zpid': 31958674,
#     'streetAddress': '4154 54th St',
#     'zipcode': '11377',
#     'city': 'Flushing',
#     'state': 'NY',
#     'latitude': 40.744181,
#     'longitude': -73.910928,
#     'price': 775000.0,
#     'dateSold': 0,
#     'bathrooms': 1.0,
#     'bedrooms': 3.0,
#     'livingArea': 663.0,
#     'yearBuilt': -1,
#     'lotSize': 1999.0,
#     'homeType': 'SINGLE_FAMILY',
#     'homeStatus': 'FOR_SALE',
#     'photoCount': 1,
#     'imageLink': 'https://photos.zillowstatic.com/p_g/ISjzq3y4adjgmp1000000000.jpg',
#     'daysOnZillow': -1,
#     'isFeatured': False,
#     'shouldHighlight': False,
#     'brokerId': 13869,
#     'zestimate': 746372,
#     'rentZestimate': 2500,
#     'listing_sub_type': {'is_FSBA': True},
#     'priceReduction': '',
#     'isUnmappable': False,
#     'mediumImageLink': 'https://photos.zillowstatic.com/p_c/ISjzq3y4adjgmp1000000000.jpg',
#     'isPreforeclosureAuction': False,
#     'homeStatusForHDP': 'FOR_SALE',
#     'priceForHDP': 775000.0,
#     'festimate': 730164,
#     'isListingOwnedByCurrentSignedInAgent': False,
#     'isListingClaimedByCurrentSignedInUser': False,
#     'hiResImageLink': 'https://photos.zillowstatic.com/p_f/ISjzq3y4adjgmp1000000000.jpg',
#     'watchImageLink': 'https://photos.zillowstatic.com/p_j/ISjzq3y4adjgmp1000000000.jpg',
#     'tvImageLink': 'https://photos.zillowstatic.com/p_m/ISjzq3y4adjgmp1000000000.jpg',
#     'tvCollectionImageLink': 'https://photos.zillowstatic.com/p_l/ISjzq3y4adjgmp1000000000.jpg',
#     'tvHighResImageLink': 'https://photos.zillowstatic.com/p_n/ISjzq3y4adjgmp1000000000.jpg',
#     'zillowHasRightsToImages': False,
#     'desktopWebHdpImageLink': 'https://photos.zillowstatic.com/p_h/ISjzq3y4adjgmp1000000000.jpg',
#     'hideZestimate': False,
#     'isPremierBuilder': False,
#     'isZillowOwned': False,
#     'currency': 'USD',
#     'country': 'USA',
#     'taxAssessedValue': 692000.0,
#     'streetAddressOnly': '4154 54th St',
#     'unit': ' '
#     }, ...
# ]

# have to filter out some rogue records
# 647  APARTMENT       NaN       750.0     -1.0
# 649  APARTMENT       NaN         NaN     -1.0
# 650  APARTMENT       NaN       850.0     -1.0
# [157 rows x 4 columns]
# ipdb> apts_valid = apts[['homeType', 'price', 'livingArea', 'lotSize']]
# filters the df

"""
temp = [m for m in map_results if "buildingId" in m]
{'buildingId': '40.744767--73.920548', 'price': 'From $398,000', 'minBeds': 1, 'minBaths': 1.0, 'minArea': 750, 'unitCount': 2, 'd
etailUrl': '/b/4310-44th-st-sunnyside-ny-5YDdtD/', 'latLong': {'latitude': 40.744767, 'longitude': -73.920548}, 'variableData': {}
, 'statusType': 'FOR_SALE', 'statusText': 'For Rent', 'listingType': '', 'isFavorite': False, 'imgSrc': 'https://photos.zillowstat
ic.com/p_e/IS7qrksmwiv47z0000000000.jpg', 'imgCount': 8, 'plid': '1455451'}

some records from map_results are not normal listing, they have subtypes inside them
for example:
    https://www.zillow.com/b/4725-40th-st-sunnyside-ny-5YDFHW/

1. we need to take this url and then get the subunits, (can we get detailed info from it or we need to use /b/.... url)
we can get this href url
<a data-test-id="bdp-property-card" class="unit-card-link" href="/homedetails/4310-44th-St-APT-6F-Sunnyside-NY-11104/245433092_zpid/">
now we just need to write crawler for this page

2. using beautiful soup and then use zillowScraper to scrap the detailed listing information
"""

df_original = pd.DataFrame.from_records(home_info_list)
df_price_not_null = df_original[df_original.price.notnull()]
df_living_area_positive = df_price_not_null[df_price_not_null.livingArea > 0]
# filter apratment size to be less than 1000, larger than 1000 on zillow seems like either co-op house or entire build for apartments?
df_living_area_apartment_size = df_price_not_null[df_price_not_null.livingArea < 1000]
df = df_living_area_apartment_size  # drops the original df to free spaces

living_area_type_df = df.groupby('homeType').livingArea.sum()
price_df = df.groupby('homeType').price.sum()
lot_size_df = df.groupby('homeType').lotSize.sum()
price_per_sqft = price_df.div(living_area_type_df)

counts = df.groupby('homeType').homeType.value_counts()
print("home type counts:")
print(counts)

apts = df[df.homeType == 'APARTMENT']
apts_tb = apts[['streetAddress', 'city', 'homeType', 'livingArea', 'price', 'lotSize']]

print("price_per_sqft:")
print(price_per_sqft)
print()


# price_per_sqft_lotsize = price_df.div(lot_size_df)
# print("price_per_sqft_lotsize:")
# print(price_per_sqft_lotsize)
# print()


print("details apartment info:")
print(apts_tb)
print()

import ipdb
ipdb.set_trace()

"""
[{'Details_Broad': {}, 'Address': {}, 'Title': '4310 44th St APT 6F, Sunnyside, NY 11104 | Zillow', 'price': 385000, 'address': '4310 44th St APT 6F', 'city': 'Sunnyside', 'state': 'NY', 'livingArea': 750, 'homeType': 'CONDO', 'lotSize': 9500, 'zestimate': 384991}, {'Details_Broad': {}, 'Address': {}, 'Title': '4310 44th St APT 6H, Sunnyside, NY 11104 | Zillow', 'price': 385000, 'address': '4310 44th St APT 6H', 'city': 'Sunnyside', 'state': 'NY', 'livingArea': 750, 'homeType': 'CONDO', 'lotSize': 9500, 'zestimate': 381098}, {'Details_Broad': {}, 'Address': {}, 'Title': '4310 44th St APT 5A, Sunnyside, NY 11104 | Zillow', 'price': 398000, 'address': '4310 44th St APT 5A', 'city': 'Sunnyside', 'state': 'NY', 'livingArea': 750, 'homeType': 'CONDO', 'lotSize': -1, 'zestimate': 390603}, {'Details_Broad': {}, 'Address': {}, 'Title': '4310 44th St APT 3B, Sunnyside, NY 11104 | Zillow', 'price': 595000, 'address': '4310 44th St APT 3B', 'city': 'Sunnyside', 'state': 'NY', 'livingArea': 1000, 'homeType': 'CONDO', 'lotSize': 9500, 'zestimate': 583590}]
"""

building_info_json = []
# now we scrap those buildings have multiple units in it
for building_info in building_info_list:
    print('checking building {}'.format(building_info))
    scrapper = sdgo_proxy.zscrapper.ZillowScraper()
    json_obj_temp = scrapper.scrap_building('http://zillow.com' + building_info['detailUrl'])
    building_info_json.extend(json_obj_temp)

pprint.pprint(building_info_json)

import ipdb
ipdb.set_trace()

building_df = pd.DataFrame(building_info_json)

building_living_area_type_df = df.groupby('homeType').livingArea.sum()
building_price_df = df.groupby('homeType').price.sum()
building_lot_size_df = df.groupby('homeType').lotSize.sum()
building_price_per_sqft = price_df.div(living_area_type_df)


aggregated_living_area_df = living_area_type_df.add(building_living_area_type_df)
aggregated_price_df = price_df.add(building_price_df)
aggregated_lot_size_df = lot_size_df.add(building_lot_size_df)
aggregated_price_per_sqft = aggregated_price_df.div(aggregated_lot_size_df)

print("final price_per_sqft:")
print(aggregated_price_per_sqft)
