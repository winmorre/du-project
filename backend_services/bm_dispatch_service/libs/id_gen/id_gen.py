"""
This helper will generate 64-bit unique identifiers
these ids will be 64-bit unsigned integers
"""
import math
import time
from uuid import getnode as get_mac

import structlog

_Logger = structlog.getLogger(__name__)

UNUSED_BITS = 0
WORKER_ID_BITS = 5
SEQUENCE_BITS = 12
Data_Center_Bit = 5
EPOCH_BITS = 20

MaxWorkerId = int(2 ** WORKER_ID_BITS) - 1

MaxSequence = int(2 ** SEQUENCE_BITS) - 1

DEFAULT_CUSTOM_EPOCH = 1680816325195
worker_shift = SEQUENCE_BITS
Time_Shift = SEQUENCE_BITS + WORKER_ID_BITS + Data_Center_Bit
Datacenter_shift = SEQUENCE_BITS + WORKER_ID_BITS


# WORKER_ID_BITS will be Mac address.
class IdGenerator:
    __slots__ = ("last_timestamp", "sequence", "worker_id", "sequence_mask", "timestamp_left_shift")

    def __init__(self):
        self.last_timestamp = -math.inf
        self.sequence = 0
        self.worker_id = IdGenerator._get_worker_id()
        self.sequence_mask = -1 ^ (-1 << SEQUENCE_BITS)
        self.timestamp_left_shift = SEQUENCE_BITS + WORKER_ID_BITS

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(IdGenerator, cls).__new__(cls)

        return cls.instance

    def next_id(self):
        current_timestamp = IdGenerator.timestamp_generator()

        if current_timestamp < self.last_timestamp:
            raise ValueError("Invalid system clock")

        if current_timestamp == self.last_timestamp:
            self.sequence = self.sequence & self.sequence_mask
            if self.sequence == 0:
                current_timestamp = self.til_next_timestamp()
        else:
            self.sequence = 0

        self.last_timestamp = current_timestamp

        new_id = current_timestamp << Time_Shift | \
                 (Data_Center_Bit << Datacenter_shift) | \
                 (self.worker_id << worker_shift) | self.sequence

        if self.sequence >= MaxSequence or self.sequence < 0:
            self.sequence = 0
        else:
            self.sequence += 1

        if self.worker_id >= MaxWorkerId:
            self.worker_id = 0

        return new_id

    @staticmethod
    def timestamp_generator():
        current_time = time.time_ns() // 1_000_000

        return current_time

    @staticmethod
    def _get_worker_id():
        worker_id = get_mac() & MaxWorkerId
        return worker_id

    def til_next_timestamp(self):
        timestamp = IdGenerator.timestamp_generator()
        while timestamp <= self.last_timestamp:
            timestamp = IdGenerator.timestamp_generator()

        return timestamp


# get this to work on multiple threads
gen = IdGenerator()


def get_id():
    new_id = gen.next_id()
    _Logger.info("New id generated", id=new_id)

    return new_id


__all__ = ["get_id"]
