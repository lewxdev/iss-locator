#!/usr/bin/env python

import turtle
from config import api_key
from datetime import datetime
from helpers import relative_fromtimestamp, create_heading, get_json


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
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        options = {"latlng": f"{lat},{lon}", "key": api_key}
        data = get_json(base_url, params=options)

        if data["status"] != "ZERO_RESULTS":
            if "compound_code" in data["plus_code"]:
                return data["plus_code"]["compound_code"].split(maxsplit=1)[1]
            for result in data["results"]:
                if "Ocean" in result["formatted_address"]:
                    return result["formatted_address"]
        return "Unknown"

    def get_info(self, output=False):
        """Retrieves information about the current state of the ISS
        (with optional print `output`) and stores in instance of `self`.
        """
        data = get_json("http://api.open-notify.org/iss-now.json")
        lat = float(data["iss_position"]["latitude"])
        lon = float(data["iss_position"]["longitude"])

        self.xy_location = lon, lat
        self.last_update = data["timestamp"]
        self.passengers = [
            astronaut["name"]
            for astronaut
            in get_json("http://api.open-notify.org/astros.json")["people"]
            if astronaut["craft"] == "ISS"
        ]

        if output:
            readable_date = relative_fromtimestamp(self.last_update)
            print(create_heading(f"ISS Information ({readable_date})"))
            self.locality = SpaceStation.get_locale_info(lat, lon)
            print(f"Above: {self.locality}")

            for unit, value in data["iss_position"].items():
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
                readable_date = relative_fromtimestamp(pass_['risetime'])
                print(f"{index + 1}. {readable_date}")

    def set_coords(self):
        """Sets the positional coordinates of the ISS turtle on screen
        to match the response coordinates from Open Notify.
        """
        if not hasattr(self, "xy_location"):
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
