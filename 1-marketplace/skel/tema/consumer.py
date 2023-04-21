"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        # get id for the cart
        self.cart_id = marketplace.new_cart()

    def run(self):
        # for the cart, get the relevant fields
        for cart in self.carts:
            for field in cart:
                field_type = field["type"]
                field_product = field["product"]
                field_quantity = field["quantity"]

                # depending on the operation type, try to add or remove
                # the given amount of each product
                if field_type == "add":
                    for _ in range(field_quantity):
                        while True:
                            # if we can add
                            if self.marketplace.add_to_cart(self.cart_id, field_product):
                                break
                            # otherwise, wait and try again
                            sleep(self.retry_wait_time)
                elif field_type == "remove":
                    for _ in range(field_quantity):
                        # remove the product from the cart
                        self.marketplace.remove_from_cart(self.cart_id, field_product)

        # finally, place the order and print the result
        with self.marketplace.lock_print_cart:
            for product in self.marketplace.place_order(self.cart_id):
                print(self.name + " bought " + str(product))
