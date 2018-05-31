from lxml import html  
import csv
import requests
import zipcode
import time
import re
import argparse
import math
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random


''' 
This program will scrape all of the phone numbers in the categories listed in the switcher function.
You can change the categories that it scrapes by going to yelp and finding the category you want to search and checking it's url.

The program will go through the categories in the same order everytime. Everytime it switches categories, it will assign a new IP address.

Also, the file will export all of phone numbers into one csv file.
This file will be named 'yelp_cityname_state_zipcode' ex. 'yelp_omaha_ne_68102'

How to run this program: 
python YelpScraper.py 92866
'''


ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]

def prox():

	proxies_req = Request('https://www.sslproxies.org/')
	proxies_req.add_header('User-Agent', ua.random)
	proxies_doc = urlopen(proxies_req).read().decode('utf8')

	soup = BeautifulSoup(proxies_doc, 'html.parser')
	proxies_table = soup.find(id='proxylisttable')

	# Save proxies in the array
	for row in proxies_table.tbody.find_all('tr'):
		proxies.append({
		'ip':   row.find_all('td')[0].string,
		'port': row.find_all('td')[1].string
		})

	# Choose a random proxy

	proxy_index = random.randint(0, len(proxies) - 1)
	proxy = proxies[proxy_index]


	req = Request('http://icanhazip.com')
	req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')

		
		# Make the call

	try:
		my_ip = urlopen(req).read().decode('utf8')
		print(my_ip)
	except: # If error, delete this proxy and find another one
		del proxies[proxy_index]
		print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
		proxy_index = random.randint(0, len(proxies) - 1)
		proxy = proxies[proxy_index]
		



def switcher(argument):
	switcher = {
	    1: 'General+Contractor',
	    2: 'Handyman',
	    3: 'Construction',
	    4: 'Roofing',
	    5: 'Garage',
	    6: 'Cabinetry',
	    7: 'Carpenter',
	    8: 'Deck+Contractor',
	    9: 'Paving+Contractor',
	    10: 'Fences',
	    11: 'Gates',
	    12: 'Fireplace',
	    13: 'Metal+Fabricator',
	    14: 'Painters',
	    15: 'Siding',
	    16: 'Staircase',
	    17: 'paver',
	    18: 'Hvac',
	    19: 'Electrician',
	    20: 'Furniture+Reupholstery',
	    21: 'Furniture+Repair',
	    22: 'Movers',
	    23: 'Pest+Control',
	    24: 'Septic+Service',
	    25: 'Pool+Service',
	    26: 'Tree+Services',
	    27: 'Carpet+Cleaning',
	    28: 'Chimney+Sweeps',
	    29: 'Home+Cleaning',
	    30: 'Junk+Removal',
	    31: 'hauling',
	    32: 'Door+Repair',
	    33: 'Locksmith',
	    34: 'Home+Builders',
	    35: 'Home+%26+Garden',
	    36: 'Appliances+%26+Repair',
	    37: 'Solar+Installation',
	    38: 'Insulation+Installation',
	    39: 'Kitchen+%26+Bath',
	    40: 'Grout+Service',
	    41: 'Window+Washing',
	    42: 'Air+Duct+Cleaning',
	    43: 'Tiling',
	    44: 'Demolition+Service',
	    45: 'Office+Cleaning',

	}
	return switcher.get(argument, "Invalid Category!")

def city_state(zip_c):

	in_zip= zipcode.isequal(zip_c)
	zip_state = in_zip.state
	zip_city = in_zip.city
	zip_city = zip_city.replace(" ","")

	file_name = "yelp_"+zip_city.lower()+"_"+zip_state.lower()+"_"+zip_c+".csv"

	return file_name


def parse(url):	

	time_delay_parse= random.uniform(.01,2)
	parse_req = Request(url)
	parse_req.add_header('User-Agent', ua.random)
	parse_doc = urlopen(parse_req).read().decode('utf8')
	time.sleep(time_delay_parse)
	parser = html.fromstring(parse_doc)
	print ("Parsing the page")
	listing = parser.xpath("//li[@class='regular-search-result']")
	scraped_datas=[]
	
	for results in listing:
		raw_position = results.xpath(".//span[@class='indexed-biz-name']/text()")
		raw_telephone = parser.xpath(".//span[@class='biz-phone']//text()")

		print("------------------------------------------------------------------------------------")


		# Get raw telephone numbers (includes advertisments)

		telephone = ''.join(raw_telephone).strip()		
		telephone = telephone.replace(" ","")
		telephone = telephone.split("\n")
		telephone = list(filter(None, telephone))

		clean_num = []
		for item in telephone:
			replaced = item.replace(")",") ")
			clean_num.append(replaced)

		for item in clean_num:	

			data={'telephone': item}
			scraped_datas.append(data)
			
		return scraped_datas


# Goes to URL and takes the total number of entries
def getTotalResults(url):

	time_delay_parse= random.uniform(.01,10)
	parse_req = Request(url)
	parse_req.add_header('User-Agent', ua.random)
	parse_doc = urlopen(parse_req).read().decode('utf8')
	time.sleep(time_delay_parse)
	parser = html.fromstring(parse_doc)
	

	raw_hasResults = parser.xpath('//*[@id="super-container"]/div/div[2]/div[1]/div/div[4]/div/div/ul/li[1]//text()')
	hasResults = ''.join(raw_hasResults).strip()
	
	if(hasResults == "Try a different location."):
		print("TRY DIFFERENT")
		total_results = 0
		return total_results

	else:	
		raw_total_results = parser.xpath("//span[@class='pagination-results-window']//text()")

		total_results = ''.join(raw_total_results).strip()
		total_results = total_results.replace(" ","")
		total_results = total_results.split("of")[1]
		total_results = int(total_results)

		return total_results

def getPageResults(url):
	time_delay_parse = random.uniform(.01,5)
	pgr_req = Request(url)
	pgr_req.add_header('User-Agent', ua.random)
	pgr_doc = urlopen(pgr_req).read().decode('utf8')
	time.sleep(time_delay_parse)
	parser = html.fromstring(pgr_doc)

	raw_hasPages = parser.xpath('//*[@id="super-container"]/div/div[2]/div[1]/div/div[4]/ul[2]/li[1]/div/div/div[1]/div/div[2]/h3/span/text()')
	hasPages = ''.join(raw_hasPages).strip()
	
	if(hasPages == "Try a different location."):
		page_results = 0
		return page_results
	else:
		page_results = 1
		return page_results


def roundUp(num):
    return num - (num%10)


def main():
	prox()
	time_delay_random = random.uniform(.01,5)
	argparser = argparse.ArgumentParser()
	argparser.add_argument('place',help = 'zip code')
	args = argparser.parse_args()
	place = args.place

	file_name = city_state(place)

	
	search_index = 1
	
	with open(file_name,"w") as fp:
				fieldnames= ['telephone']
				writer = csv.DictWriter(fp,fieldnames=fieldnames)
				writer.writeheader()

	while search_index < 46:
		try:

			
			page_number = 0
			search_query = switcher(search_index)

			print("Page: %s -- Category: %s"%(page_number,search_query))
			
			# First Page of telephone numbers placed into .csv
			yelp_url = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,page_number)
			

			time.sleep(time_delay_random)
			total_results = getTotalResults(yelp_url)
			page_results = getPageResults(yelp_url)

			print("TOTAL RESULTS = ",total_results)
			last_page = roundUp(total_results)
			print("LAST PAGE = ", last_page)

			if total_results > 0 and page_results > 0:
				prox()
				print ("Retrieving :",yelp_url)
				scraped_data = parse(yelp_url)
				with open(file_name,"a") as fp:
					fieldnames= ['telephone']
					writer = csv.DictWriter(fp,fieldnames=fieldnames)
					writer.writeheader()
					for data in scraped_data:
						writer.writerow(data)
						print(data)
				page_number += 10

				# Second to last pages places into .csv

				if total_results >= 1000:
					while page_number < 981:
						prox()
						yelp_url = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,page_number)

						print ("Retrieving :",yelp_url)
						scraped_data = parse(yelp_url)
						print ("Writing data to output file")
						with open(file_name,"a") as fp:
							writer = csv.DictWriter(fp,fieldnames=fieldnames)
							for data in scraped_data:
								writer.writerow(data)
						page_number += 10

				else :
					while page_number < last_page: # <last page = 21
						prox()
						# last page inaccurate

						print(("PAGE NUMBER:%s < LAST PAGE:%s")%(page_number,last_page))

						yelp_url = "https://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s"%(search_query,place,page_number)
						print ("Retrieving :",yelp_url)

						scraped_data = parse(yelp_url)
						print ("Writing data to output file")
						with open(file_name,"a") as fp:
							writer = csv.DictWriter(fp,fieldnames=fieldnames)
							for data in scraped_data:
								writer.writerow(data)
						page_number += 10
				search_index += 1
				
			else:
				search_index += 1
				
		except TypeError:
			search_index += 1
			
			
			pass			

if __name__=="__main__":
	main()
