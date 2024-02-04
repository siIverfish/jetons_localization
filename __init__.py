#!/usr/bin/env python3

""" 
    This script will subscribe to the RoboRIO odometry feed;
    perform localization code; and publish final location of
    the robot on the field to NetworkTables so that 
    the RoboRIO can *know where it is!*

    Uses piped iterators for all processing.
"""

import ntcore
import rclpy

from typing import Iterator

from .odometry_position_subscriber import OdometryPositionSubscriber
from .apriltag_position_subscriber import AprilTagPositionSubscriber
from .new_position_publisher import NewPositionPublisher
from .localizer import Localizer

TABLE_NAME = "jetson"
NT_INSTANCE = ntcore.NetworkTableInstance.getDefault()
NT_TABLE = NT_INSTANCE.getTable(TABLE_NAME)

def run(iterable):
    """ Consume an iterable. """
    for _ in iterable:
        pass

def initialize_iterator() -> Iterator[None]:
    # Set up inputs, localizer, and output
    odometry_position_subscriber = OdometryPositionSubscriber(instance=NT_INSTANCE, table=NT_TABLE)
    apriltag_position_subscriber = AprilTagPositionSubscriber()
    localizer = Localizer()
    new_position_publisher = NewPositionPublisher(table=NT_TABLE)

    # setup iterator flow path
    # odometry_position_subscriber = map(lambda x: (print(x),x)[1], odometry_position_subscriber)
    final_positions = map(localizer, apriltag_position_subscriber)
    published_values = map(new_position_publisher, final_positions)
    return published_values

def main(args=None):
    rclpy.init(args=args)
    iterator = initialize_iterator()
    try:
        # start pulling values through the iterator chain
        run(iterator)
    except KeyboardInterrupt:
        print("Ctrl-C detected, shutting down...")
    finally:
        # really it doesn't matter if this code is in the `except` or `finally` block
        # todo: failing to shut down?
        rclpy.shutdown()
        print("rclpy.shutdown() called successfully.")


if __name__ == "__main__":
    main()
