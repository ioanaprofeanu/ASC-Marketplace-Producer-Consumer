Name: Profeanu Ioana
Group: 333CA

# Homework 1 ASC - Marketplace
##### Implemented a simulation of the MPMC problem in Python by simulating a real-life marketplace.

Solution:
-
* The marketplace was implemented so that it keeps track of the producers' and customers' buffers.
A dictionary was used for each, which has the id (cart id or producer id) as key and a list of
products (for producers) or a tuple of products and their producer's id (for customers) as value.
The marketplace also has a reference to all locks used throughout the implementation, including a
dictionary of locks for each producer's id.
* A lock was used for each function to handle race conditions. More details on the "Locks
usage by method" section.
* The register returns an individual id for each producer and is called when initializing the
producer's fields.
* For publishing, first we check if the current producer's buffer is full; if not, we add the new
product. The producer, depending on the result of the publishing function called for a current
product, waits an adequate number of seconds.
* For adding to the cart, we look into all producers' buffers for the current product; if found, we
remove it from the buffer and add it as a tuple, alongside with the producer's id, to the
customer's buffer.
* The remove from cart does the opposite of the add: it looks for the product in the customer's
buffer and, if found, moves it to the producer's buffer. Both functions are called by the customer
while iterating through the cart. If the functions return false, the customer waits.
* For placing the order, simply get a list of all products within the customer's buffer, which will
be printed by him.
* The unittesting was created in a manner that allows for an independent run. For that, the buffers
for the producers’ and customers' data were reinitialized at the beginning of each test.
* The logging was done using RotatingFileHandler for keeping a log history and using GMT.

***Locks usage by method***
* In the register_producer method, the lock_register_producer was used because there can be
multiple producers trying to register at once. The lock ensures that each producer gets a
different id.
* Similarly, in the new_cart method, the lock_new_cart was used to ensure each customer gets an
individual cart id.
* In the publish method, the producer's lock from producers_locks_dictionary because, even if each
producer has its own buffer, a customer can search for an item in its buffer or return a product,
thus existing the possibility of race condition.
* In the same manner, in add_to_cart and remove_from_cart methods, the locks from
producers_locks_dictionary were used as the customer is iterating through each of the producers'
buffers.
* Finally, lock_print_cart was used for when the customers print their list to stdout, so only
one can print at a time.

Implementation
-
* All the task's requirements and functionalities were implemented, including the optimal usage of
locks, usage of loggers, unittesting, and git for code versioning (found in the git section).
* Because the solution uses different buffers for each producer, each producer can individually add
products without any race conditions. Similarly, when a customer looks for a product/ puts back a
product, only the current producer's buffer is locked. This results in an efficient parallel
implementation.
* Logging and unittesting were very useful for debugging and understanding the program flow,
helping me find a few concurrency bugs.
* Unittesting should be run from the skel directory, using the command: python3 -m unittest
tema/marketplace.py

Resources
-
1. https://docs.python.org/3/library/unittest.html#organizing-test-code
2. https://stackoverflow.com/questions/6321160/how-to-set-timestamps-on-gmt-utc-on-python-logging
3. https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler
4. https://docs.python.org/3/howto/logging.html
5. https://ocw.cs.pub.ro/courses/apd/laboratoare/05
6. Github Copilot was used for text prediction for commenting on the code.

Git
-
* https://github.com/ioanaprofeanu/Marketplace-ASC-Homework1
* .git: https://drive.google.com/drive/folders/1_eElbvq0_CpgirKFqKQ_EjUZHtgGzJHQ?usp=share_link
