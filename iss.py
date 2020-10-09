#!/usr/bin/env python

__author__ = "J. Lewis, @lewxdev"

import turtle
from helpers import create_heading, get_json
from SpaceStation import SpaceStation
from Window import Window


def main():
    window = Window((-180, -90, 180, 90), "map.gif")
    # latitude/longitude bounds: 180 and 90deg respectively
    window.draw_grid(size=15)

    print(create_heading("ISS Locator"))
    print("GUI displaying the current location of the ISS")
    print("usage:")
    print("- Red pin is your current location")
    print("- Click it to get the next overhead passes")
    print("- Click on the ISS to display it's information")

    user = get_json("https://ipinfo.io/")
    user_location = tuple(map(lambda n: float(n), user["loc"].split(",")))

    pin = turtle.Turtle("circle", visible=False)
    pin.penup()
    pin.color("red")
    pin.shapesize(0.4)
    pin.setposition(user_location[::-1])
    pin.showturtle()

    iss = SpaceStation(window.screen)
    pin.onclick(lambda x, y: iss.get_next_pass(*pin.pos()[::-1], output=True))
    window.screen.mainloop()


if __name__ == '__main__':
    main()
