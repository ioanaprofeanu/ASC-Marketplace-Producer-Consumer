"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock
import unittest
import time
import logging
import logging.handlers

from .product import Tea, Coffee
from .consumer import Consumer
from .producer import Producer

# initialize the logger for the INFO level, with a rotating file handler
logger = logging.getLogger()
logging.basicConfig(
    handlers=[logging.handlers.RotatingFileHandler('marketplace.log', mode='a',
                maxBytes=1024*1024, backupCount=10, encoding=None, delay=False)],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%d/%m/%Y %I:%M:%S %p')
# format the time as UTC time
logging.Formatter.converter = time.gmtime

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
        logger.info("Called constructor with queue_size_per_producer = %s.", \
                    queue_size_per_producer)

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

        logger.info("Done calling constructor.")

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        logger.info("Called register_producer.")
        # get lock of the producers dictionary; get a new id depending on the dictionary's size
        with self.lock_register_producer:
            current_producer_id = len(self.producers_dictionary)
            self.producers_dictionary[current_producer_id] = []
            new_producer_lock = Lock()
            self.producers_locks_dictionary[current_producer_id] = new_producer_lock
            logger.info("Done calling register_producer; assigned the id = %s.",
                        current_producer_id)
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
        # get lock of the producer's buffer
        with self.producers_locks_dictionary[producer_id]:
            # if the buffer is not full, add the product
            if len(self.producers_dictionary[producer_id]) < self.queue_size_per_producer:
                self.producers_dictionary[producer_id].append(product)
                logger.info("Done calling publish; added the product to the producer's buffer.")
                return True
        logger.info("Done calling publish; buffer full, failed to add.")
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        logger.info("Called new_cart.")
        # get lock of the carts dictionary; allocate a new id depending on the dictionary's size
        with self.lock_new_cart:
            current_cart_id = len(self.carts_dictionary)
            self.carts_dictionary[current_cart_id] = []
            logger.info("Done calling new_cart; assigned the cart_id = %s.", current_cart_id)
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
        logger.info("Called add_to_cart with parameters cart_id = %s, product = %s.",\
                    cart_id, product)

        # try to find the product in the producers' buffers
        for key, value in self.producers_dictionary.items():
            # get lock of the current producer's buffer
            with self.producers_locks_dictionary[key]:
                # if found, remove it from the producer's buffer and add it to the cart
                if product in value:
                    new_product_tuple = (product, key)
                    value.remove(product)
                    self.carts_dictionary[cart_id].append(new_product_tuple)
                    logger.info("Done calling add_to_cart; found and added product to the cart.")
                    return True
        logger.info("Done calling add_to_cart; failed to find product.")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logger.info("Called remove_from_cart with parameters cart_id = %s, product = %s.", \
                    cart_id, product)
        # find the product in the cart
        for product_tuple in self.carts_dictionary[cart_id]:
            # if found, remove it from the cart and add it back to the producer's buffer
            if product_tuple[0] == product:
                self.carts_dictionary[cart_id].remove(product_tuple)
                # get lock of the current producer's buffer
                with self.producers_locks_dictionary[product_tuple[1]]:
                    self.producers_dictionary[product_tuple[1]].append(product)
                logger.info("Done calling remove_from_cart; removed product and added it back.")
                return
        logger.info("Done calling remove_from_cart; product not found.")

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logger.info("Called place_order with parameter cart_id = %s.", cart_id)
        # put each product in the cart in a list and return it
        order_items = []
        for product_tuple in self.carts_dictionary[cart_id]:
            order_items.append(product_tuple[0])
        logger.info("Done calling place_order; the cart items are: %s.", order_items)
        return order_items

class TestMarketplace(unittest.TestCase):
    """
    Class for unittesting the marketplace module
    """
    def setUp(self):
        """
        Initialize the marketplace, the products, producers and consumers
        """
        self.marketplace = Marketplace(10)

        self.product_1 = Coffee(name = "Indonezia", acidity = 5.05,\
                        roast_level = "MEDIUM", price = 1)
        self.product_2 = Coffee(name = "Brazil", acidity = 4.05, \
                        roast_level = "LIGHT", price = 5)
        self.product_3 = Tea(name = "Wild Cherry", type = "Black", price = 3)

        self.producer_1 = Producer(products = [[self.product_1, 8, 0.1], \
                        [self.product_2, 4, 0.2]], marketplace = self.marketplace, \
                        republish_wait_time = 0.3)
        self.producer_2 = Producer(products = [[self.product_3, 5, 0.1]], \
                        marketplace = self.marketplace, republish_wait_time = 0.3)

        self.consumer_1 = Consumer(carts = [
            {
                "type": "add",
                "product": self.product_1,
                "quantity": 3
            },
            {
                "type": "add",
                "product": self.product_3,
                "quantity": 5
            },
            {
                "type": "add",
                "product": self.product_2,
                "quantity": 1
            },
            {
                "type": "remove",
                "product": self.product_2,
                "quantity": 1
            },
            {
                "type": "remove",
                "product": self.product_1,
                "quantity": 1
            }
        ], marketplace = self.marketplace, retry_wait_time = 0.3)

        self.consumer_2 = Consumer(carts = [
            {
                "type": "add",
                "product": self.product_3,
                "quantity": 3
            }
        ], marketplace = self.marketplace, retry_wait_time = 0.3)

    def test_register_producer(self):
        """
        Test the register_producer method
        """
        self.assertEqual(len(self.marketplace.producers_dictionary), 2)
        self.assertEqual(self.producer_1.producer_id, 0)
        self.assertEqual(self.producer_2.producer_id, 1)
        self.assertEqual(self.marketplace.register_producer(), 2)
        self.assertEqual(self.marketplace.register_producer(), 3)

    def test_publish(self):
        """
        Test the publish method
        """
        # initialize each producers' buffer
        self.marketplace.producers_dictionary[self.producer_1.producer_id] = []
        self.marketplace.producers_dictionary[self.producer_2.producer_id] = []

        total_products_producer_1 = self.producer_1.products[0][1] + self.producer_1.products[1][1]
        # publish products for producer 1; keep track if the number of products
        # is above the queue size; test the results
        for i in range(0, total_products_producer_1):
            current_product = self.product_1
            if i > 4:
                current_product = self.product_2
            if i < self.marketplace.queue_size_per_producer:
                self.assertTrue(self.marketplace.publish(self.producer_1.producer_id, \
                                current_product))
                self.assertEqual(len(self.marketplace.producers_dictionary\
                                [self.producer_1.producer_id]), i + 1)
            else:
                self.assertFalse(self.marketplace.publish(self.producer_1.producer_id, \
                                current_product))
                self.assertEqual(len(self.marketplace.producers_dictionary\
                                [self.producer_1.producer_id]),\
                                self.marketplace.queue_size_per_producer)

        # publish products for producer 2; the number of products is below the queue size;
        # check the results
        total_products_producer_2 = self.producer_2.products[0][1]
        for i in range(0, total_products_producer_2):
            self.assertTrue(self.marketplace.publish(self.producer_2.producer_id, self.product_3))
            self.assertEqual(len(self.marketplace.producers_dictionary\
                            [self.producer_2.producer_id]), i + 1)

    def test_new_cart(self):
        """
        Test the new_cart method
        """
        self.assertEqual(len(self.marketplace.carts_dictionary), 2)
        self.assertEqual(self.consumer_1.cart_id, 0)
        self.assertEqual(self.consumer_2.cart_id, 1)
        self.assertEqual(self.marketplace.new_cart(), 2)
        self.assertEqual(self.marketplace.new_cart(), 3)

    def test_add_to_cart(self):
        """
        Test the add_to_cart method
        """
        # initialize buffers
        self.marketplace.producers_dictionary[self.producer_2.producer_id] = []
        self.marketplace.carts_dictionary[self.consumer_2.cart_id] = []
        total_products_producer_2 = self.producer_2.products[0][1]

        # publish products
        for _ in range(0, total_products_producer_2):
            self.marketplace.publish(self.producer_2.producer_id, self.product_3)
        # add products to cart and test the results
        for i in range (0, total_products_producer_2):
            self.assertTrue(self.marketplace.add_to_cart(self.consumer_2.cart_id, self.product_3))
            self.assertEqual(len(self.marketplace.carts_dictionary\
                            [self.consumer_2.cart_id]), i + 1)
            self.assertEqual(len(self.marketplace.producers_dictionary\
                            [self.producer_2.producer_id]), total_products_producer_2 - i - 1)
        self.assertFalse(self.marketplace.add_to_cart(self.consumer_2.cart_id, self.product_3))

    def test_remove_from_cart(self):
        """
        Test the remove_from_cart method
        """
        # initialize buffers
        self.marketplace.producers_dictionary[self.producer_2.producer_id] = []
        self.marketplace.carts_dictionary[self.consumer_2.cart_id] = []
        total_products_producer_2 = self.producer_2.products[0][1]

        # publish products and add them to cart
        for _ in range(0, total_products_producer_2):
            self.marketplace.publish(self.producer_2.producer_id, self.product_3)
        for _ in range (0, total_products_producer_2):
            self.assertTrue(self.marketplace.add_to_cart(self.consumer_2.cart_id, self.product_3))

        # remove products from cart and test the results
        self.marketplace.remove_from_cart(self.consumer_2.cart_id, self.product_3)
        self.marketplace.remove_from_cart(self.consumer_2.cart_id, self.product_3)
        self.assertEqual(len(self.marketplace.carts_dictionary[self.consumer_2.cart_id]), \
                        total_products_producer_2 - 2)
        self.assertEqual(len(self.marketplace.producers_dictionary\
                        [self.producer_2.producer_id]), 2)

    def test_place_order(self):
        """
        Test the place_order method
        Add a fiew products to the cart, remove some of them and then place the order
        """
        # initialize buffers
        self.marketplace.producers_dictionary[self.producer_1.producer_id] = []
        self.marketplace.carts_dictionary[self.consumer_1.cart_id] = []

        total_product_1 = 4
        total_product_2 = 3

        # publish products
        for _ in range(0, total_product_1):
            self.marketplace.publish(self.producer_1.producer_id, self.product_1)
        for _ in range(0, total_product_2):
            self.marketplace.publish(self.producer_1.producer_id, self.product_2)

        # add/remove products to/from cart
        for _ in range(0, total_product_1):
            self.marketplace.add_to_cart(self.consumer_1.cart_id, self.product_1)
        for _ in range(0, total_product_2):
            self.marketplace.add_to_cart(self.consumer_1.cart_id, self.product_2)
        self.marketplace.remove_from_cart(self.consumer_1.cart_id, self.product_1)

        # place order and test the result
        order = self.marketplace.place_order(self.consumer_1.cart_id)
        self.assertEqual(len(order), 6)
