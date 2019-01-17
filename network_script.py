from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import ipaddress
from netaddr import *
import re
import datetime

URI = 'https://nettools.net.berkeley.edu/pubtools/info/campusnetworks.html'

PAGE_TEXT = """Campus Networks IP Addresses

Last updated: {}

======================================================================================\n"""


def display_to_page():
  today_date = datetime.date.today()
  text_body = PAGE_TEXT.format(today_date)
  return text_body

def scrape_page():
  uClient = uReq(URI)
  pageHTML = uClient.read()
  uClient.close()
  pageSoup = soup(pageHTML, "html.parser")
  return pageSoup

def generate_ip_list(ipRows):
  #Take a list of ipv4 ip addresses in CIDR notation, i.e. 128.32.0.0/16
  #Generate a list of ranges starting from first to last, i.e. 128.32.0.0-128.32.255.255
  ipList = ''
  for ip in ipRows:
    cidr_ip = IPNetwork(ip)
    start = cidr_ip[0]
    end = cidr_ip[-1]
    range_display = str(start) + '-' + str(end)
    ipList += range_display + ", "
  #Remove trailing ", " 
  ipList = ipList[:-2]
  return ipList


#Gather page content using BeautifulSoup
pageSoup = scrape_page()

#Navigate to main content
mainContainer = pageSoup.find("div", {"id": "ucbito_main_container"})
#Retrieve first h2 header
firstHeader = mainContainer.select_one("h2:nth-of-type(1)").text

if firstHeader == 'Full List of Campus Networks':
  #Select only the first table
  ipTable = mainContainer.select_one("table:nth-of-type(1)")
  allRowsValues = []
  allRows = [[ele.text.strip() for ele in item.find_all("td")]
    for item in ipTable.find_all("tr")]
  for k in allRows:
    allRowsValues.append(k)
  #Remove the first two header rows that do not contain ip addresses
  del allRowsValues[0]
  del allRowsValues[0]
  #Collect all the ip address rows and remove superscript and ipv6 address
  ipRows = []
  for v in allRowsValues:
    rowText = v[0]
    bitNum = rowText.split("/",1)[1]
    superscriptList = ['241','82','322']
    haystack = "2607"
    if haystack not in rowText:
      if bitNum not in superscriptList:
        ipRows.append(v[0])
      else:
        v[0] = v[0].replace('241', '24')
        v[0] = v[0].replace('82', '8')
        v[0] = v[0].replace('322', '32')
        ipRows.append(v[0])

  outputList = generate_ip_list(ipRows)

  output = display_to_page()
  fileText = output + outputList
  text_file = open("output.txt", "w")
  text_file.write("%s" % fileText)
  text_file.close()
else:
	print('error')

