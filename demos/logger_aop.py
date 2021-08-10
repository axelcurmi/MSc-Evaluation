import aspectlib
import logging

logging.basicConfig()
logger = logging.getLogger("origami")
logger.setLevel(logging.DEBUG)

# Create the rollback table
_rollback_table = {}

@aspectlib.Aspect
def handle_aspect(*args, **kwargs):
    print("  -> in the Handler.handle function")
    try:
        yield
    finally:
        _rollback_table["HANDLE_ASPECT"].rollback()
        del _rollback_table["HANDLE_ASPECT"]
        
_rollback_table["HANDLE_ASPECT"] = aspectlib.weave(
    logging.Handler.handle, handle_aspect)

logger.log(logging.DEBUG, "This is my message..")
logger.log(logging.DEBUG, "This is my message..")
