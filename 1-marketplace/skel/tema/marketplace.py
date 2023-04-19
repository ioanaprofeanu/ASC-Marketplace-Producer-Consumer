"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock
import time
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
		handlers=[RotatingFileHandler('./marketplace.log', maxBytes=100000, backupCount=15,
				mode='a')],
		level=logging.INFO,
		format="[%(asctime)s] %(levelname)s %(message)s")
logging.Formatter.converter = time.gmtime
logger = logging.getLogger()


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
		logger.info("Called constructor with queue_size_per_producer = %s.", queue_size_per_producer)

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

		logger.info("Finished calling constructor.")

	def register_producer(self):
		"""
		Returns an id for the producer that calls this.
		"""
		logger.info("Called register_producer.")

		with self.lock_register_producer:
			current_producer_id = len(self.producers_dictionary)
			self.producers_dictionary[current_producer_id] = []
			new_producer_lock = Lock()
			self.producers_locks_dictionary[current_producer_id] = new_producer_lock
			logger.info("Finished calling register_producer; assigned the current producer the id = %s.", current_producer_id)
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
		logger.info("Called publish with producer_id = %s and product = %s.", producer_id, product)
		with self.producers_locks_dictionary[producer_id]:
			if len(self.producers_dictionary[producer_id]) < self.queue_size_per_producer:
				self.producers_dictionary[producer_id].append(product)
				logger.info("Finished calling publish; successfully added the product to the producer's buffer.")
				return True
			else:
				logger.info("Finished calling publish; the producer's buffer is full, failed to add to buffer.")
				return False

	def new_cart(self):
		"""
		Creates a new cart for the consumer

		:returns an int representing the cart_id
		"""
		logger.info("Called new_cart.")
		with self.lock_new_cart:
			current_cart_id = len(self.carts_dictionary)
			self.carts_dictionary[current_cart_id] = []
			logger.info("Finished calling new_cart; assigned the current consumer the cart_id = %s.", current_cart_id)
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
		logger.info("Called add_to_cart with parameters cart_id = %s, product = %s.", cart_id, product)

		for key in self.producers_dictionary:
			with self.producers_locks_dictionary[key]:
				if product in self.producers_dictionary[key]:
					new_product_tuple = (product, key)
					self.producers_dictionary[key].remove(product)
					self.carts_dictionary[cart_id].append(new_product_tuple)
					logger.info("Finished calling add_to_cart; successfully found and added the product to the cart.")
					return True
		logger.info("Finished calling add_to_cart; finding the product in the producers' buffers failed.")
		return False

	def remove_from_cart(self, cart_id, product):
		"""
		Removes a product from cart.

		:type cart_id: Int
		:param cart_id: id cart

		:type product: Product
		:param product: the product to remove from cart
		"""
		logger.info("Called remove_from_cart with parameters cart_id = %s, product = %s.", cart_id, product)
		for product_tuple in self.carts_dictionary[cart_id]:
			if product_tuple[0] == product:
				self.carts_dictionary[cart_id].remove(product_tuple)
				with self.producers_locks_dictionary[product_tuple[1]]:
					self.producers_dictionary[product_tuple[1]].append(product)
				logger.info("Finished calling remove_from_cart; successfully removed the product from the cart and added it to the eproducer's buffer.")
				return

	def place_order(self, cart_id):
		"""
		Return a list with all the products in the cart.

		:type cart_id: Int
		:param cart_id: id cart
		"""
		logger.info("Called place_order with parameter cart_id = %s.", cart_id)
		order_items = []
		for product_tuple in self.carts_dictionary[cart_id]:
			order_items.append(product_tuple[0])
		logger.info("Finished calling place_order; returning the list of products in the cart.")
		return order_items
		
