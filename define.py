#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
from pprint import pprint

class HTMLNavigationError(Exception): pass

def _search_url(search_term):
	url_format = "https://www.google.com/search?q=DEFINE:{term}"
	search_term = '"'.join(['', search_term, '']).translate({ord(' '): '%20'})
	return url_format.format(term=search_term)

def _get_defns(defn_table):
	meaning_dict = {}
	for row in defn_table.find_all('tr'):
		data = row.find('td')
		pos = data.find('div')
		if pos:
			meaning_list_node = data.find('ol')
			meaning_dict[pos.string] = [meaning.string for meaning in 
				meaning_list_node.find_all('li')]
	return meaning_dict

def _meaning_tables(search_full):
	try:
		search_results = search_full.find('tbody', id='desktop-search').find(id='search').find('div', 'g')
		first = search_results.find('div')
	except: raise HTMLNavigationError('Error reading search results.')
	return first.find_all('table')

def define(search_term):
	req = requests.get(_search_url(search_term))
	full = BeautifulSoup(req.text, 'lxml')
	meaning_tables = _meaning_tables(full)
	if meaning_tables:
		return list(map(_get_defns, meaning_tables))

def interactive_prompt(prompt='Define: '):
	inp = lambda: input(prompt)
	val = inp()
	while val: 
		yield val
		val = inp()

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Dynamic word lookup using Google.')
	parser.add_argument('-d', '--define', nargs='+', default=None, 
		help='Search for a specific term or terms. Prints results as a JSON dictionary.')
	args = parser.parse_args()
	if args.define:
		import json
		result_dict = {search_term: define(search_term) for search_term in args.define}
		print(json.dumps(result_dict))
	else:
		for search_term in interactive_prompt():
			pprint(define(search_term))