"""
Class const for the vClass
Used to define permissions on certain road parts. For documentation:
http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes#Abstract_Vehicle_Class
"""
class VClass(enumerate):
    IGNORING = "ignoring"
    PRIVATE = "private"
    EMERGENCY = "emergency"
    AUTHORITY = "authority"
    ARMY = "army"
    VIP = "vip"
    PASSENGER = "passenger"
    HOV = "hov"
    TAXI = "taxi"
    BUS = "bus"
    COACH = "coach"
    DELIVERY = "delivery"
    TRUCK = "truck"
    TRAILER = "trailer"
    TRAM = "tram"
    RAIL_URBAN = "rail_urban"
    RAIL = "rail"
    RAIL_ELECTRIC = "rail_electric"
    MOTORCYCLE = "motorcycle"
    MOPED = "moped"
    BICYCLE = "bicycle"
    PEDESTRIAN = "pedestrian"
    EVEHICLE = "evehicle"
    SHIP = "ship"

"""
Class const for the vehicle's GUI shape
Used to show certain vehicles with a certain shape in sumo's GUI.
http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes#Abstract_Vehicle_Class
"""
class GuiShape(enumerate):
    PEDESTRIAN = "pedestrian"
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    PASSENGER = "passenger"
    PASSENGER_SEDAN = "passenger/sedan"
    PASSENGER_HATCHBACK = "passenger/hatchback"
    PASSENGER_WAGON = "passenger/wagon"
    PASSENGER_VAN = "passenger/van"
    DELIVERY = "delivery"
    TRUCK = "truck"
    TRUCK_SEMITRAILER = "truck/semitrailer"
    TRUCK_TRAILER = "truck/trailer"
    BUS = "bus"
    BUS_CITY = "bus/city"
    BUS_FLEXIBLE = "bus/flexible"
    BUS_OVERLAND = "bus/overland"
    RAIL = "rail"
    RAIL_LIGHT = "rail/light"
    RAIL_CITY = "rail/city"
    RAIL_SLOW = "rail/slow"
    RAIL_FAST = "rail/fast"
    RAIL_CARGO = "rail/cargo"
    EVEHICLE = "evehicle"
    SHIP = "ship"

"""
A class which simulates a SUMO car types
An object created contains most variables a SUMO car types can have. For documentation:
http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes#Vehicle_Types
"""
class VehicleType:

    def __init__(self, id):
        self.id = id
        self.acceleration = 2.6
        self.deceleration = 4.5
        self.sigma = 0.5
        self.length = 5.0
        self.minGap = 2.5
        self.maxSpeed = 70.0
        self.vClass = VClass.PASSENGER
        self.guiShape = GuiShape.PASSENGER
        self.impatience = 0.0
        self.speedFactor = 1

    def printXML(obj):
        xmlString = "<vType"
        for attr in dir(obj):
            if hasattr(obj, attr) and "_" not in attr and not callable(getattr(obj,attr)):
                xmlString += (" %s=\"%s\"" % (attr, getattr(obj, attr)))
        xmlString += "/>"
        return xmlString