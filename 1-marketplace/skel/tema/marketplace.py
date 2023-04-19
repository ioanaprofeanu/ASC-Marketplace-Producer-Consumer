"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock

class Marketplace:
	"""
	Class that represents the Marketplace. It's the central part of the implementation.
	The producers and consumers use its methods concurrently.
	"""
	def __init__(self, queue_size_per_producer):
		"""
		Constructor

		:type queue_size_per_producer: Int
		:param queue_size_per_producer: the maximum size of a queue associated with each producer
		"""
		self.queue_size_per_producer = queue_size_per_producer

  		# dictionary of producers' buffers 
		self.producers_dictionary = {}
		# dictionary of locks for each producer's buffer
		self.producers_locks_dictionary = {}
  
		# dictionary of consumers' carts
		self.carts_dictionary = {}

		# lock for registering a new producer
		self.lock_register_producer = Lock()
		# lock for creating a new cart
		self.lock_new_cart = Lock()
		# lock for printing cart
		self.lock_print_cart = Lock()

	def register_producer(self):
		"""
		Returns an id for the producer that calls this.
		"""
		with self.lock_register_producer:
			current_producer_id = len(self.producers_dictionary)
			self.producers_dictionary[current_producer_id] = []
			new_producer_lock = Lock()
			self.producers_locks_dictionary[current_producer_id] = new_producer_lock
			return current_producer_id

	def publish(self, producer_id, product):
		"""
		Adds the product provided by the producer to the marketplace

		:type producer_id: Integer
		:param producer_id: producer id

		:type product: Product
		:param product: the Product that will be published in the Marketplace

		:returns True or False. If the caller receives False, it should wait and then try again.
		"""
		with self.producers_locks_dictionary[producer_id]:
			if len(self.producers_dictionary[producer_id]) < self.queue_size_per_producer:
				self.producers_dictionary[producer_id].append(product)
				return True
			return False

	def new_cart(self):
		"""
		Creates a new cart for the consumer

		:returns an int representing the cart_id
		"""
		with self.lock_new_cart:
			current_cart_id = len(self.carts_dictionary)
			self.carts_dictionary[current_cart_id] = []
			return current_cart_id

	def add_to_cart(self, cart_id, product):
		"""
		Adds a product to the given cart. The method returns

		:type cart_id: Int
		:param cart_id: id cart

		:type product: Product
		:param product: the product to add to cart

		:returns True or False. If the caller receives False, it should wait and then try again
		"""
		for key in self.producers_dictionary:
			with self.producers_locks_dictionary[key]:
				if product in self.producers_dictionary[key]:
					new_product_tuple = (product, key)
					self.producers_dictionary[key].remove(product)
					self.carts_dictionary[cart_id].append(new_product_tuple)
					return True
		return False

	def remove_from_cart(self, cart_id, product):
		"""
		Removes a product from cart.

		:type cart_id: Int
		:param cart_id: id cart

		:type product: Product
		:param product: the product to remove from cart
		"""
		for product_tuple in self.carts_dictionary[cart_id]:
			if product_tuple[0] == product:
				self.carts_dictionary[cart_id].remove(product_tuple)
				with self.producers_locks_dictionary[product_tuple[1]]:# s ar putea sa existe cazul cand buffer ul e full si nu mai pot sa adaug
					self.producers_dictionary[product_tuple[1]].append(product)
				return

	def place_order(self, cart_id):
		"""
		Return a list with all the products in the cart.

		:type cart_id: Int
		:param cart_id: id cart
		"""
		order_items = []
		for product_tuple in self.carts_dictionary[cart_id]:
			order_items.append(product_tuple[0])
		return order_items
		
