import math
from geo.map_square import MapSquare


class Geo(object):
    @classmethod
    def calculate_map_squares(cls, top_left_position, bottom_right_position, meters=1000):
        # 1. Calculate all latitudes steps for given range of x meters (default 1km)
        # the difference between latitude degree ≈ 111km
        # https://en.wikipedia.org/wiki/Geographic_coordinate_system

        # Todo: Exception handling and the cases that the ranges are outside europa
        meters_step_to_degree = float(meters) / 111000.0
        diff_latitude = math.fabs(top_left_position[0] - bottom_right_position[0])
        latitude_steps = int((diff_latitude * 111000.0) / float(meters) + 0.5)
        latitudes = list(map(lambda x: bottom_right_position[0] + (meters_step_to_degree * x), range(latitude_steps)))

        map_squares = []
        diff_longitude = math.fabs(bottom_right_position[1] - top_left_position[1])

        for index, latitude in enumerate(latitudes):
            if index < (len(latitudes) - 1):
                top_latitude = latitudes[index + 1]
                bottom_latitude = latitude
                longitude_degrees_range_bottom = cls.longitude_degrees_for_meters(bottom_latitude, meters)
                longitude_degrees_range_top = cls.longitude_degrees_for_meters(top_latitude, meters)

                longitude_steps = int((diff_longitude / longitude_degrees_range_bottom) + 0.5)

                for step in range(longitude_steps):
                    top_longitude = top_left_position[1] + (longitude_degrees_range_top * step)
                    bottom_longitude = top_left_position[1] + (longitude_degrees_range_bottom * (step + 1))
                    map_squares.append(MapSquare(top_right=[top_latitude, bottom_longitude],
                                                 bottom_left=[bottom_latitude, top_longitude]))
        return map_squares

    @classmethod
    def longitude_degrees_for_meters(cls, latitude, meters):
        longitude_meters = (math.pi / 180.0) * 6367.449 * math.cos(
            latitude)  # 1. calculate longitude meters for given latitude

        # Relativer Längengrad abhängig von seinem Längengradabstand zwischen 100% = 111km
        return (float(meters) * longitude_meters) / (111.0 * 1000.0 * longitude_meters)
