#!/usr/bin/env python

import turtle
from datetime import datetime
from helpers import create_heading, get_json


class SpaceStation:
    """Provides methods for manipulating the ISS turtle"""
    def __init__(self, screen, img="iss.gif", path_color="red"):
        """Initializes a unique ISS turtle on the given `screen`"""
        assert isinstance(screen, turtle._Screen), "`screen` must be _Screen"
        self.screen = screen

        for turtle_ in screen.turtles():
            assert turtle_.shape() != img, "ISS already initialized on screen"

        self.screen.register_shape(img)
        self.turtle = turtle.Turtle(img, visible=False)
        self.turtle.penup()
        self.turtle.pencolor(path_color)
        self.turtle.onclick(lambda *coords: SpaceStation.get_info(output=True))
        self.turtle.setposition(SpaceStation.get_coords())
        self.turtle.showturtle()
        self.turtle.pendown()

        self.init_updater()

    def get_info(output=False):
        """Returns the data received from Open Notify about the current
        location of the ISS (with optional print `output`).
        """
        data = get_json("http://api.open-notify.org/iss-now.json")
        assert data["message"] == "success", "API call failed"

        if output:
            as_of = datetime.fromtimestamp(data["timestamp"])
            print(create_heading(f"ISS Information ({as_of})"))

            geo_coords = data["iss_position"].values()
            geo_coords = tuple(map(lambda n: float(n), geo_coords))
            locale = SpaceStation.get_locale_info(*geo_coords)

            locale_city, locale_state = (locale['city'],
                                         locale['principalSubdivision'])
            locale_bound = locale["localityInfo"]["informative"][0]

            if "Ocean" in locale_bound["name"]:
                print(f"Above: {locale_bound['name']}")
            elif locale_city and locale_state:
                print(f"Above: {locale_city}, {locale_state}")
            else:
                print("Above: Unknown")

            for unit, value in data["iss_position"].items():
                print(f"{unit.capitalize()}: {value}")

            passengers = SpaceStation.get_passengers()
            if passengers:
                print("Passengers:")
                for astro in passengers:
                    print(f"\t- {astro['name']}")
        return data

    def get_passengers():
        """Returns a list of astronauts aboard the ISS"""
        data = get_json("http://api.open-notify.org/astros.json")
        assert data["message"] == "success", "API call failed"
        return [astro for astro in data["people"] if astro["craft"] == "ISS"]

    def get_locale_info(lat, lon):
        """Returns locality information for the given `lat` and `lon`"""
        base = "https://api.bigdatacloud.net/data/reverse-geocode-client"
        options = {"latitude": lat, "longitude": lon}
        return get_json(base, params=options)

    def get_next_pass(self, lat, lon, output=False):
        """Returns the data received from Open Notify about the next
        pass of the ISS for a given `lat` and `lon` (with optional
        `output`).
        """
        base = "http://api.open-notify.org/iss-pass.json"
        options = {"lat": lat, "lon": lon}
        next_pass = get_json(base, params=options)
        assert next_pass["message"] == "success", "API call failed"

        if output:
            locale = SpaceStation.get_locale_info(lat, lon)

            locale_city, locale_state = (locale['city'],
                                         locale['principalSubdivision'])
            locale_bound = locale["localityInfo"]["informative"][0]

            if "Ocean" in locale_bound["name"]:
                print(create_heading(f"Next Pass ({locale_bound['name']})"))
            elif locale_city and locale_state:
                print(create_heading(
                    f"Next Pass ({locale_city}, {locale_state})"))
            else:
                print(create_heading("Next Pass (Unknown)"))

            for index, pass_ in enumerate(next_pass["response"]):
                print(f"{index + 1}. {datetime.fromtimestamp(pass_['risetime'])}")
        return next_pass

    def get_coords():
        """Returns the ISS coordinates as `(x, y)` where `x` is the
        current longitude and `y` is the current latitude.
        """
        data = SpaceStation.get_info()
        lat, lon = data["iss_position"].values()
        return tuple(map(lambda n: float(n), (lat, lon)))[::-1]
        # map the strings as a tuple pair of floats (reversed)

    def set_coords(self):
        """Sets the positional coordinates of the ISS turtle on screen
        to match the response coordinates from Open Notify.
        """
        x0, y0 = self.turtle.position()
        x1, y1 = SpaceStation.get_coords()

        horz_dist = sum(map(lambda n: abs(n), (x0, x1)))
        vert_dist = sum(map(lambda n: abs(n), (y0, y1)))

        if horz_dist > 180 or vert_dist > 90:
            self.turtle.penup()
        self.turtle.setposition(x1, y1)
        self.turtle.pendown()
        return self.turtle.position()

    def init_updater(self, interval=5000):
        """Once called, the turtle's positional coordinates will be
        updated on screen at a given `interval`
        """
        self.set_coords()
        self.screen.ontimer(self.init_updater, interval)
