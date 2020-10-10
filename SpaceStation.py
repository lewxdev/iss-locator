#!/usr/bin/env python

import turtle
from datetime import datetime
from helpers import create_heading, get_json


class SpaceStation:
    """Provides methods for manipulating the ISS turtle"""
    def __init__(self, screen, img="iss.gif", path_color="red"):
        """Initializes a unique ISS turtle on the given `screen`"""
        assert isinstance(screen, turtle._Screen), "`screen` must be _Screen"
        for turtle_ in screen.turtles():
            assert turtle_.shape() != img, "ISS already initialized on screen"

        self.passes = {}
        self.screen = screen
        self.screen.register_shape(img)

        self.turtle = turtle.Turtle(img, visible=False)
        self.turtle.penup()
        self.turtle.pencolor(path_color)
        self.turtle.onclick(lambda *coords: self.get_info(output=True))

        self.init_updater()
        self.turtle.pendown()
        self.turtle.showturtle()

    def get_locale_info(lat, lon):
        """Returns locality information for the given `lat` and `lon`"""
        base_url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
        data = get_json(base_url, params={"latitude": lat, "longitude": lon})

        locality = data["locality"]
        state = data["principalSubdivision"]

        for props in data["localityInfo"].values():
            for prop in props:
                if prop["name"] in ("Ocean", "Sea"):
                    waters = prop["name"]
                    break
            else:
                continue
            break

        return locality or state or waters or "Unknown"

    def get_info(self, output=False):
        """Retrieves information about the current state of the ISS
        (with optional print `output`) and stores in instance of `self`.
        """
        positional_data = get_json("http://api.open-notify.org/iss-now.json")
        self.geo_location = positional_data["iss_position"]
        self.last_update = positional_data["timestamp"]

        geo_coords = [float(unit) for unit in self.geo_location.values()]
        self.xy_location = geo_coords[::-1]
        self.locality = SpaceStation.get_locale_info(*geo_coords)
        self.passengers = [
            astronaut["name"]
            for astronaut
            in get_json("http://api.open-notify.org/astros.json")["people"]
            if astronaut["craft"] == "ISS"
        ]

        if output:
            readable_date = datetime.fromtimestamp(self.last_update)
            print(create_heading(f"ISS Information ({readable_date})"))
            print(f"Above: {self.locality}")

            for unit, value in self.geo_location.items():
                print(f"{unit.capitalize()}: {value}")
            if self.passengers:
                print("Passengers:")
                for astronaut in self.passengers:
                    print(f"\t- {astronaut}")

    def get_next_pass(self, lat, lon, output=False):
        """Returns the data received from Open Notify about the next
        pass of the ISS for a given `lat` and `lon` (with optional
        `output`).
        """
        base_url = "http://api.open-notify.org/iss-pass.json"
        next_pass = get_json(base_url, params={"lat": lat, "lon": lon})

        if output:
            locality = SpaceStation.get_locale_info(lat, lon)
            print(create_heading(f"Next Pass ({locality})"))

            for index, pass_ in enumerate(next_pass["response"]):
                readable_date = datetime.fromtimestamp(pass_['risetime'])
                print(f"{index + 1}. {readable_date}")
        self.passes[(lat, lon)] = next_pass

    def set_coords(self):
        """Sets the positional coordinates of the ISS turtle on screen
        to match the response coordinates from Open Notify.
        """
        if not hasattr(self, "position"):
            self.get_info()
            self.turtle.setposition(*self.xy_location)
        else:
            self.get_info()
            x0, y0 = self.turtle.position()
            x1, y1 = self.xy_location

            if x0 * x1 <= 0 or y0 * y1 <= 0:
                self.turtle.penup()
                self.turtle.setposition(x1, y1)
                self.turtle.pendown()
            else:
                self.turtle.setposition(x1, y1)

    def init_updater(self, interval=5000):
        """Once called, the turtle's positional coordinates will be
        updated on screen at a given `interval`
        """
        self.set_coords()
        self.screen.ontimer(self.init_updater, interval)
