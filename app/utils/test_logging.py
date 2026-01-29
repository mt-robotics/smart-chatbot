import logging

# Create our formatter with both correct and incorrect attributes
logger = logging.getLogger("test_logger")
logger.setLevel(logging.DEBUG)

# Create a handler that writes to the console
handler = logging.StreamHandler()
logger.addHandler(handler)

# Test 1: Correct attributes
print("\nTest 1: Correct attributes:")
formatter1 = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
handler.setFormatter(formatter1)
logger.info("This is a test message")

# Test 2: Incorrect attributes
print("\nTest 2: Incorrect attributes:")
formatter2 = logging.Formatter(
    "%(asc_time)s - %(log_name)s - %(level)s - %(file)s:%(line_no)d - %(msg)s"
)
handler.setFormatter(formatter2)
logger.info("This is another test message")
