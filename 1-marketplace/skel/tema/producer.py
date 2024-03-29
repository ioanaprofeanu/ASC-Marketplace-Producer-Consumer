"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        # register the producer
        self.producer_id = marketplace.register_producer()

    def run(self):
        while True:
            # for each product
            for product in self.products:
                product_id = product[0]
                product_quantity = product[1]
                product_wait_time = product[2]

                # depending on the quantity, try to publish the product
                for _ in range(product_quantity):
                    while True:
                        # if we can publish
                        if self.marketplace.publish(self.producer_id, product_id):
                            sleep(product_wait_time)
                            break
                        # otherwise, wait and try again
                        sleep(self.republish_wait_time)
