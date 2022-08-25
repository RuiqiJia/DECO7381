from enum import Enum

class Status(Enum):
    NO_REQUEST = 0
    REQUEST_SENT = 1
    REQUEST_RECEIVED = 2
    REQUEST_ACCEPTED = 3
