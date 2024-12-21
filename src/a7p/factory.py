"""
This module provides a set of data structures and a factory class for constructing a Payload
for ballistic profiling. The data structures represent various components, such as metadata,
cartridge information, zeroing data, atmosphere conditions, barrel specifications, and bullet
properties, which are used to generate a payload for ballistic calculations.

It includes the following components:

1. **DistanceTable Enum**:
   A collection of predefined distance ranges for various ballistic profiles, such as subsonic,
   low range, medium range, long range, and ultra range.

2. **Meta Class**:
   Stores metadata related to the profile, including the profile name, short names, and user notes.

3. **Zeroing Class**:
   Represents zeroing data, such as the X, Y coordinates, pitch, and distance for the zeroing process.

4. **Atmosphere Class**:
   Contains data about the atmospheric conditions, such as temperature, pressure, and humidity.

5. **Barrel Class**:
   Describes the barrel characteristics, including caliber, sight height, twist, and twist direction.

6. **Cartridge Class**:
   Defines a cartridge with properties like name, muzzle velocity, temperature, and powder sensitivity.

7. **DragPoint NamedTuple**:
   A named tuple for representing drag coefficient and velocity data used in ballistic calculations.

8. **Bullet Class**:
   Describes the bullet's properties, including its name, diameter, weight, length, and drag model.

9. **Switches NamedTuple**:
   Defines the switch positions, each containing a position with parameters for zoom, distance, and c_idx.

10. **A7PFactory Class**:
    A factory class that generates a Payload for ballistic calculations based on various data inputs.
    It takes the input parameters for the profile and generates a `profedit_pb2.Payload` instance,
    validating and formatting the input data as necessary.

Usage:
    The `A7PFactory` can be used to generate a `profedit_pb2.Payload` by passing instances of the
    data classes (e.g., `Meta`, `Barrel`, `Bullet`, etc.) to its constructor.

Dependencies:
    - `a7p.profedit_pb2`: Protobuf definitions for the payload and ballistic parameters.
"""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

from a7p import profedit_pb2


class DistanceTable(Enum):
    """
    Enum representing predefined distance ranges for ballistic profiling.
    The ranges represent typical distances for different ballistic scenarios
    (subsonic, low range, medium range, long range, and ultra range).
    """
    SUBSONIC = (  # 25-400
        25, 50, 75, 100, 110, 120, 130, 140, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220,
        225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300, 305, 310, 315, 320, 325, 330,
        335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390, 395, 400,
    )
    LOW_RANGE = (  # 100-700
        100, 150, 200, 225, 250, 275, 300, 320, 340, 360, 380, 400, 410, 420, 430, 440,
        450, 460, 470, 480, 490, 500, 505, 510, 515, 520, 525, 530, 535, 540, 545, 550,
        555, 560, 565, 570, 575, 580, 585, 590, 595, 600, 605, 610, 615, 620, 625, 630,
        635, 640, 645, 650, 655, 660, 665, 670, 675, 680, 685, 690, 695, 700
    )
    MEDIUM_RANGE = (  # 100 - 1000
        100, 200, 250, 300, 325, 350, 375, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 610, 620, 630, 640,
        650, 660, 670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 805, 810, 815, 820, 825, 830,
        835, 840, 845, 850, 855, 860, 865, 870, 875, 880, 885, 890, 895, 900, 905, 910, 915, 920, 925, 930, 935, 940,
        945, 950, 955, 960, 965, 970, 975, 980, 985, 990, 995, 1000
    )
    LONG_RANGE = (  # 100 - 1700
        100, 200, 250, 300, 350, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 610, 620, 630, 640, 650, 660,
        670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 810, 820, 830, 840, 850, 860, 870, 880,
        890, 900, 910, 920, 930, 940, 950, 960, 970, 980, 990, 1000, 1005, 1010, 1015, 1020, 1025, 1030, 1035, 1040,
        1045, 1050, 1055, 1060, 1065, 1070, 1075, 1080, 1085, 1090, 1095, 1100, 1105, 1110, 1115, 1120, 1125, 1130,
        1135, 1140, 1145, 1150, 1155, 1160, 1165, 1170, 1175, 1180, 1185, 1190, 1195, 1200, 1205, 1210, 1215, 1220,
        1225, 1230, 1235, 1240, 1245, 1250, 1255, 1260, 1265, 1270, 1275, 1280, 1285, 1290, 1295, 1300, 1305, 1310,
        1315, 1320, 1325, 1330, 1335, 1340, 1345, 1350, 1355, 1360, 1365, 1370, 1375, 1380, 1385, 1390, 1395, 1400,
        1405, 1410, 1415, 1420, 1425, 1430, 1435, 1440, 1445, 1450, 1455, 1460, 1465, 1470, 1475, 1480, 1485, 1490,
        1495, 1500, 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565, 1570, 1575, 1580,
        1585, 1590, 1595, 1600, 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655, 1660, 1665, 1670,
        1675, 1680, 1685, 1690, 1695, 1700,
    )
    ULTRA_RANGE = (
        100, 200, 250, 300, 350, 400, 450, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780,
        800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090,
        1100, 1110, 1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210, 1220, 1230, 1240, 1250, 1260, 1270,
        1280, 1290, 1300, 1310, 1320, 1330, 1340, 1350, 1360, 1370, 1380, 1390, 1400, 1410, 1420, 1430, 1440, 1450,
        1460, 1470, 1480, 1490, 1500, 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565,
        1570, 1575, 1580, 1585, 1590, 1595, 1600, 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655,
        1660, 1665, 1670, 1675, 1680, 1685, 1690, 1695, 1700, 1705, 1710, 1715, 1720, 1725, 1730, 1735, 1740, 1745,
        1750, 1755, 1760, 1765, 1770, 1775, 1780, 1785, 1790, 1795, 1800, 1805, 1810, 1815, 1820, 1825, 1830, 1835,
        1840, 1845, 1850, 1855, 1860, 1865, 1870, 1875, 1880, 1885, 1890, 1895, 1900, 1905, 1910, 1915, 1920, 1925,
        1930, 1935, 1940, 1945, 1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015,
        2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065,
    )


@dataclass
class Meta:
    """
    Class representing the metadata for the ballistic profile, including profile name, short
    names, and user notes.
    """
    name: str = 'New profile'
    short_name_top: str = ''
    short_name_bot: str = ''
    user_note: str = ''


@dataclass
class Zeroing:
    """
    Class representing zeroing data, including X, Y coordinates, pitch, and zero distance.
    """
    x: float = 0
    y: float = 0
    pitch: float = 0
    distance: float = 100


@dataclass
class Atmosphere:
    """
    Class representing atmospheric data, including temperature, pressure, and humidity.
    """
    temperature: int = 15
    pressure: int = 1000
    humidity: int = 50


@dataclass
class Barrel:
    """
    Class representing the barrel specifications, including caliber, sight height, twist, and
    twist direction.
    """
    caliber: str = 'New caliber'
    sight_height: int = 90
    twist: float = 9.
    twist_dir: profedit_pb2.TwistDir = profedit_pb2.TwistDir.RIGHT


@dataclass
class Cartridge:
    """
    Class representing a cartridge with properties such as name, muzzle velocity, temperature,
    and powder sensitivity.
    """
    name: str = "New cartridge"
    muzzle_velocity: float = 800.
    temperature: int = 15
    powder_sens: float = 1.5


class DragPoint(NamedTuple):
    """
    A named tuple representing drag coefficient and velocity data for ballistic calculations.
    """
    coeff: float
    velocity: float


@dataclass
class Bullet:
    """
    Class representing bullet properties, including name, diameter, weight, length, and drag model.
    """
    name: str = "New bullet"
    diameter: float = 0.308
    weight: float = 178.
    length: float = 1.2
    drag_type: profedit_pb2.GType = profedit_pb2.GType.G7
    drag_model: tuple[DragPoint] = (DragPoint(1., 0.),)


class Switches(NamedTuple):
    """
    A named tuple representing the switch positions, each containing a position with parameters
    for zoom, distance, and c_idx.
    """
    s1: profedit_pb2.SwPos = profedit_pb2.SwPos(c_idx=255, zoom=1, distance=10000)
    s2: profedit_pb2.SwPos = profedit_pb2.SwPos(c_idx=255, zoom=2, distance=20000)
    s3: profedit_pb2.SwPos = profedit_pb2.SwPos(c_idx=255, zoom=3, distance=30000)
    s4: profedit_pb2.SwPos = profedit_pb2.SwPos(c_idx=255, zoom=4, distance=100000)


class A7PFactory:
    """
    A factory class for generating a Payload for ballistic calculations based on input data
    such as metadata, zeroing, atmosphere, barrel, cartridge, bullet, and distance tables.
    """

    def __new__(cls,
                meta: Meta = Meta(),
                barrel: Barrel = Barrel(),
                cartridge: Cartridge = Cartridge(),
                bullet: Bullet = Bullet(),
                zeroing: Zeroing = Zeroing(),
                zero_atmo: Atmosphere = Atmosphere(),
                zero_powder_temp: int = 15,
                distances: [DistanceTable, tuple[float]] = DistanceTable.LONG_RANGE,
                switches: Switches = Switches()
                ) -> profedit_pb2.Payload:

        """
        Creates and returns a Payload for ballistic calculations based on the input data.

        Args:
            meta: Metadata for the profile.
            zeroing: Zeroing data for the profile.
            zero_atmo: Atmospheric conditions for the profile.
            barrel: Barrel specifications for the profile.
            cartridge: Cartridge information for the profile.
            bullet: Bullet specifications for the profile.
            distances: Predefined distance table for the profile.

        Returns:
            A `profedit_pb2.Payload` instance representing the ballistic profile.
        """

        def fmt_bottom():
            if meta.short_name_bot:
                return meta.short_name_bot
            return "{:.{}f}".format(bullet.weight, 0 if bullet.weight % 1 == 0 else 1) + 'gr'

        def drag_model():
            return [
                profedit_pb2.CoefRow(
                    bc_cd=round(point.coeff * 10000),
                    mv=round(point.velocity * 10)
                ) for point in bullet.drag_model
            ]

        if isinstance(distances, DistanceTable):
            _distances = distances.value
        elif isinstance(distances, tuple):
            _distances = distances
        else:
            raise ValueError("Distances have to be an instance of DistanceTable or tuple[float]")
        if len(_distances) < 1:
            raise ValueError("List of distances can't be empty")
        zero_dist_idx = _distances.index(round(zeroing.distance))

        return profedit_pb2.Payload(
            profile=profedit_pb2.Profile(
                profile_name=meta.name,
                cartridge_name=cartridge.name,
                bullet_name=bullet.name,

                short_name_top=meta.short_name_top if meta.short_name_top else meta.name[:6],
                short_name_bot=meta.short_name_bot if meta.short_name_bot else fmt_bottom(),
                user_note=meta.user_note,

                zero_x=round(zeroing.x * -1000),  # click_x * -1000
                zero_y=round(zeroing.y * 1000),  # click_y * 1000
                sc_height=barrel.sight_height,  # mm
                r_twist=round(barrel.twist * 100),  # Inch * 100

                c_muzzle_velocity=round(cartridge.muzzle_velocity * 10),  # MPS * 10
                c_zero_temperature=cartridge.temperature,  # C
                c_t_coeff=round(cartridge.powder_sens * 1000),  # % * 1000
                c_zero_air_temperature=zero_atmo.temperature,
                c_zero_air_pressure=round(zero_atmo.pressure * 10),  # hPa * 10
                c_zero_air_humidity=zero_atmo.humidity,  # %
                c_zero_p_temperature=zero_powder_temp,  # C
                c_zero_w_pitch=round(zeroing.pitch * 10),  # degree * 10

                b_diameter=round(bullet.diameter * 1000),  # Inch * 1000
                b_weight=round(bullet.weight * 10),  # grain * 10
                b_length=round(bullet.length * 1000),  # Inch * 1000

                twist_dir=barrel.twist_dir,
                bc_type=bullet.drag_type,  # G1, G7, CUSTOM

                switches=list(switches),
                distances=[round(d * 100) for d in _distances],
                c_zero_distance_idx=zero_dist_idx if zero_dist_idx else 0,
                coef_rows=drag_model(),

                caliber=barrel.caliber
            )
        )

    Meta = Meta
    Barrel = Barrel
    Cartridge = Cartridge
    Bullet = Bullet
    Zeroing = Zeroing
    Atmosphere = Atmosphere
    DistanceTable = DistanceTable
    Switches = Switches
    DragPoint = DragPoint


__all__ = ('A7PFactory',)
