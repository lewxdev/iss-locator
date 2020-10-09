#!/usr/bin/env python

import turtle


class Window:
    """Provides methods for manipulating the tkinter/turtle window/screen"""
    def __init__(self, bounds, bg):
        """Initialize the tkinter/turtle window/screen for interfacing.

        `kwargs` is a dictionary where each key is a method of a _Screen,
        and each value is a list of required arguments to be passed in.
        """
        self.screen = turtle.Screen()

        assert isinstance(bounds, tuple), "`bounds` must be a tuple"
        for n in bounds:
            assert isinstance(n, (int, float)), "`bounds` content not digit"
        assert len(bounds) == 4, "`bounds` must only have 4 values"
        self.bounds = bounds
        self.screen.setworldcoordinates(*self.bounds)

        assert isinstance(bg, str), "`bg` must be a str"
        if "." in bg:
            assert bg.endswith(".gif"), "`bg` must be .gif image"
            self.screen.bgpic(bg)
        else:
            self.screen.bgcolor(bg)

    def draw_line(self, x=None, y=None):
        """Draws a non-diagonal line onscreen for a given bounding box

        The optional parameters `x` and `y` are mutually exclusive and
        one must be set, specifying the line to be drawn.
        """
        lhb, lvb, uhb, uvb = self.bounds

        pen = turtle.Turtle(visible=False)
        pen.speed(0)
        pen.penup()

        assert x is not None or y is not None, "Neither `x` or `y` are set"

        if x is not None:
            assert isinstance(x, (int, float)), "`x` is not a valid number"
            pen.setposition(x, lvb)
            pen.pendown()
            pen.sety(uvb)
        else:
            assert isinstance(y, (int, float)), "`y` is not a valid number"
            pen.setposition(lhb, y)
            pen.pendown()
            pen.setx(uhb)
        pen.penup()

    def draw_grid(self, size=10):
        abs_vb, abs_hb = self.bounds[2:]

        for n in range(0, abs_hb + 1, size):
            if n != 0:
                for coord in n, -n:
                    Window.draw_line(self, y=coord)
            else:
                Window.draw_line(self, y=n)

        for n in range(0, abs_vb + 1, size):
            if n != 0:
                for coord in n, -n:
                    Window.draw_line(self, x=coord)
            else:
                Window.draw_line(self, x=n)
