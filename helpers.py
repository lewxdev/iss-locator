#!/usr/bin/env python

import requests


def create_heading(text, symbol="-", occurs=8):
    """Returns a print-ready heading string used for logging.

    This helper method accepts one required argument: `text` (the
    heading text), and two optional arguments: `symbol` (the symbol
    to be used as the heading delimiter) and `occurs` (the number of
    occurances of the surrounding delimiter)

    E.g. "-------- Example Heading --------"
    """
    assert isinstance(occurs, int), f"`occurs` is not an int, got {occurs}"
    delimiter = str(symbol) * occurs
    return f"{delimiter} {text} {delimiter}"


def get_json(query_url, params={}):
    """Uses the requests library to perform a GET request on a
    `query_url` and returns the response as JSON data.

    If `params` provided, they will be appended to the end of the
    `query_url`.
    """
    assert isinstance(query_url, str), "`query_url` must be str"
    if params:
        assert isinstance(params, dict), "`params` must be dict"

        query_options = []
        for param, value in params.items():
            assert isinstance(param, str), "API parameters must be str"
            query_options.append(f"{param}={value}")

        if not query_url.endswith("?"):
            query_url = f"{query_url}?"

        query_url = f"{query_url}{'&'.join(query_options)}"

    response = requests.get(query_url)
    return response.json()
