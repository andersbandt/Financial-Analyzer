# import needed packages
#import gobject
import os
import xml.dom.minidom
from xml.sax.saxutils import escape


"""
Categories represents the possible financial categories set in categories.xml and sub_categories.xml
categories.xml contains all the master categories
sub_categories.xml contains all the children categories
"""
class Category:

	def __init__(self, xml_category):
		self.parent = None
		self.name = None
		self.keyword = []
		self.description = None
		self.xml_content = xml_category
		self.load(xml_category)


	def load_from_string(self, string):
		dom = xml.dom.minidom.parseString(string)
		self._load(dom)

	def load(self, xml_category):
		parentPop = False # check if the parent variable is populated
		namePop = False
		keyword_populated = False
		descriptionPop = False

		# iterate through all child nodes
		for node in xml_category.childNodes:
			data = None
			if node.nodeName in ["parent", "name", "keyword", "description"]:
				try:
					data = node.childNodes[0].data
				except IndexError:
					pass

				if node.nodeName == "parent":
					self.parent = data
				elif node.nodeName == "name":
					self.name = data
				elif node.nodeName == "keyword":
					self.keyword.append(data)
					keyword_populated = True
				elif node.nodeName == "description":
					self.description = data

		if not keyword_populated:
			print("Uh oh, Category object " + self.name + " loaded in without keyword populated")

		return None 


	# printCategory: prints a categories name to the console
	def printCategory(self):
		#print("Category parent: " + self.parent)
		string_to_print = "Category name: " + self.name

		return string_to_print

	# getName: gets the name of a category
	def getName(self):
		return self.name



##############################################################################
####      VARIOUS FUNCTIONS    ###############################################
##############################################################################

# load_categories: returns an array containing all the category objects
def load_categories(filename):
	print("Loading categories from " + filename)
	categories = []  # initialize array that will be populated with Category objects
	dom = xml.dom.minidom.parse(filename)
	collection = dom.getElementsByTagName("collection")  # search for root element of tag 'collection'
	if len(collection) != 1:
            raise Exception("Wrong number of collections in XML document!")
	collection = collection[0] # not sure if this is required

	for node in collection.childNodes:
		if node.nodeName in "category":
			#try:
			categories.append(Category(node))
			#except:
			#	pass

	return categories

# load_sub_categories: returns an array containing all the


def check_categories(categories_array):
	for category in categories_array:
		if category.keyword == None:
			print("Uh oh, category: " + category.name + " has no keywords associated with it")


def print_categories(categories_array):
	for category in categories_array:
		category.print()


# get_category_strings: returns an array containing strings of all the category names
def get_category_strings(categories_array):
	category_names = []
	for category in categories_array:
		category_names.append(category.getName())

	return category_names

