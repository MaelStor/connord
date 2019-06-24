# vim: set fileencoding=utf-8 :

# connord - connect to nordvpn servers
# Copyright (C) 2019  Mael Stor <maelstor@posteo.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# here's a one liner to create this dictionary of country codes from
# nordvpn's api
# curl https://api.nordvpn.com/server 2>/dev/null | python -m json.tool | \
# grep 'flag\|country' | perl -ne 'print unless $seen{$_}++' | \
# sed -E -e 's/^        //' -e 's/("flag": )(".*")/\1\L\2/' -e 's/^"flag": //' \
# -e 's/^"country": //' | sed 's/,/:/;n' | paste - - -d' ' | tr '"' "'" | sort | \
# head -c -2 | sed -e '$a\'

from connord import ConnordError
from connord.formatter import Formatter

COUNTRIES = {
    "ae": "United Arab Emirates",
    "al": "Albania",
    "ar": "Argentina",
    "at": "Austria",
    "au": "Australia",
    "ba": "Bosnia and Herzegovina",
    "be": "Belgium",
    "bg": "Bulgaria",
    "br": "Brazil",
    "ca": "Canada",
    "ch": "Switzerland",
    "cl": "Chile",
    "cr": "Costa Rica",
    "cy": "Cyprus",
    "cz": "Czech Republic",
    "de": "Germany",
    "dk": "Denmark",
    "ee": "Estonia",
    "eg": "Egypt",
    "es": "Spain",
    "fi": "Finland",
    "fr": "France",
    "gb": "United Kingdom",
    "ge": "Georgia",
    "gr": "Greece",
    "hk": "Hong Kong",
    "hr": "Croatia",
    "hu": "Hungary",
    "id": "Indonesia",
    "ie": "Ireland",
    "il": "Israel",
    "in": "India",
    "is": "Iceland",
    "it": "Italy",
    "jp": "Japan",
    "kr": "South Korea",
    "lu": "Luxembourg",
    "lv": "Latvia",
    "md": "Moldova",
    "mk": "North Macedonia",
    "mx": "Mexico",
    "my": "Malaysia",
    "nl": "Netherlands",
    "no": "Norway",
    "nz": "New Zealand",
    "pl": "Poland",
    "pt": "Portugal",
    "ro": "Romania",
    "rs": "Serbia",
    "se": "Sweden",
    "sg": "Singapore",
    "si": "Slovenia",
    "sk": "Slovakia",
    "th": "Thailand",
    "tr": "Turkey",
    "tw": "Taiwan",
    "ua": "Ukraine",
    "us": "United States",
    "vn": "Vietnam",
    "za": "South Africa",
}


class CountryError(ConnordError):
    """Raised within this module"""


def verify_countries(countries):
    """Verify if a list of countries are valid

    :param countries: a list of countries to verify
    :returns: True if all countries are valid
    :raises CountryError: if one country in the list is invalid
    """

    if not isinstance(countries, list):
        raise TypeError(
            "Invalid format for countries: {!s} must be {!s}".format(
                type(countries), list
            )
        )

    wrong_countries = [
        country for country in countries if country.lower() not in COUNTRIES.keys()
    ]

    if wrong_countries:
        if len(wrong_countries) == 1:
            error_message = "Invalid country: {!r}".format(wrong_countries[0])
        else:
            countries_s = ""
            for country in wrong_countries:
                countries_s += "{!r},".format(country)

            error_message = "Invalid countries: {}.".format(countries_s.rstrip(","))

        raise CountryError(error_message)

    return True


# TODO: if countries are present twice this should filter countries to that
# specific country. I.e. when using the netflix option adding a country flag
# should narrow down the results instead of ignoring the double flag.
def filter_servers(servers, countries=None):
    """
    Filter a list of servers by country. If multiple countries are given
    match servers in country1 OR country2 OR ...

    :param servers: List of servers as parsed from nordvpn api in json format
    :param countries: List of countries to filter the server list. If None or
                     list is empty it returns all servers.
    :returns: The filtered list
    """

    if servers is None:
        raise TypeError("Servers may not be None")

    if countries is None or not countries or not servers:
        return servers

    countries_lower = [str.lower(country) for country in countries]

    # TODO: test if list comprehension is faster
    filtered_servers = []
    servers = servers.copy()
    for server in servers:
        flag = server["flag"].lower()
        for country in countries_lower:
            if country == flag:
                filtered_servers.append(server)
                break

    return filtered_servers


class CountriesPrettyFormatter(Formatter):
    """Format countries in pretty format"""

    def format_headline(self, sep="="):
        """Returns the centered headline filled with sep"""
        countries_header = "Countries"
        return self.center_string(countries_header, sep)

    def format_country(self, country_code, country):
        """Returns the formatted country string"""
        return "  {:6}{}".format(country_code, country)


def to_string(stream=False):
    """Gather all countries  in a printable string

    :param stream: If True print to stdout else print to formatter.output variable
    :returns: Formatted string if stream is False else an empty string
    """

    formatter = CountriesPrettyFormatter()
    file_ = formatter.get_stream_file(stream)

    headline = formatter.format_headline()
    print(headline, file=file_)

    for country_code, country in COUNTRIES.items():
        formatted_country = formatter.format_country(country_code, country)
        print(formatted_country, file=file_)

    print(formatter.format_ruler(sep="-"), file=file_)
    return formatter.get_output()


def print_countries():
    """Prints all possible countries"""
    to_string(stream=True)
