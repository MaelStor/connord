# pylint: disable=redefined-outer-name, unused-argument, unused-import, import-error

import pytest
from connord import areas
from main_test_module import (
    MockBase,
    get_stub,
    get_servers_stub,
    get_json,
    get_expected_servers_by_domain,
)


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    areas.get_locations.cache_clear()


@pytest.fixture(scope="module")
def location():
    return get_stub("location_rome_fixture.json")


@pytest.fixture(scope="module")
def location_json():
    return get_json("location_rome_fixture.json")


@pytest.fixture()
def sleepless(monkeypatch):
    def sleep(seconds):
        pass

    monkeypatch.setattr(areas.time, "sleep", sleep)


@pytest.fixture(scope="module")
def servers():
    return get_servers_stub()


@pytest.fixture()
def connection(mocker):
    return mocker.MagicMock()


@pytest.fixture
def server():
    server = {"location": {"lat": "40.123", "long": "50.321"}}
    return server


@pytest.fixture
def areas_good_fix():
    return ["min", "che"]


@pytest.fixture
def areas_not_exist():
    return ["xxxxx", "abcde"]


@pytest.fixture
def areas_ambigouous():
    return []


@pytest.fixture
def locations_db_fix():
    minneapolis = {
        "latitude": "44.98",
        "longitude": "-93.2636111",
        "display_name": (
            "The Depot Renaissance Minneapolis Hotel, "
            "3rd Avenue South, St Anthony West, Phillips, Minneapolis, "
            "Hennepin County, Minnesota, 55404, USA"
        ),
        "city": "Minneapolis",
        "country": "United States",
        "country_code": "us",
    }
    chennai = {
        "latitude": "13.083333",
        "longitude": "80.283333",
        "display_name": (
            "Chennai Fort, Muthuswamy Road, Ward 60, Zone 5 Royapuram, "
            "Chennai, Chennai district, Tamil Nadu, 600108, India"
        ),
        "city": "Chennai",
        "country": "India",
        "country_code": "in",
    }

    return [minneapolis, chennai]


@pytest.fixture
def locations_db_output():
    expected_output = """================================================================================
Mini ID :    Latitude        Longitude     City
Address
================================================================================
'm'     :   44.980000000°  -93.263611100°  Minneapolis                             
The Depot Renaissance Minneapolis Hotel, 3rd Avenue South, St Anthony West, Phillips, Minneapolis, Hennepin County, Minnesota, 55404, USA
--------------------------------------------------------------------------------
'c'     :   13.083333000°   80.283333000°  Chennai                                 
Chennai Fort, Muthuswamy Road, Ward 60, Zone 5 Royapuram, Chennai, Chennai district, Tamil Nadu, 600108, India
--------------------------------------------------------------------------------
"""
    return expected_output


@pytest.fixture
def locations_db_fix2():
    minneapolis = {
        "latitude": "44.98",
        "longitude": "-93.2636111",
        "display_name": (
            "The Depot Renaissance Minneapolis Hotel, "
            "3rd Avenue South, St Anthony West, Phillips, Minneapolis, "
            "Hennepin County, Minnesota, 55404, USA"
        ),
        "city": "Minneapolis",
        "country": "United States",
        "country_code": "us",
    }
    minnea = {
        "latitude": "88.98",
        "longitude": "-103.2636111",
        "display_name": (
            "The Depot Hotel, "
            "3rd Avenue North, St Anthony East, Phillips, Minnea, "
            "Hennepin County, Minnesota, 55404, USA"
        ),
        "city": "Minnea",
        "country": "United States",
        "country_code": "us",
    }
    return [minneapolis, minnea]


def test_query_location(sleepless, location, requests_mock):
    expected_useragent = (
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) "
        "Gecko/20100101 Firefox/60.0"
    )
    header = {"User-Agent": expected_useragent}
    latitude = "50.321"
    longitude = "60.123"
    expected_url = (
        "https://nominatim.openstreetmap.org/reverse.php?lat={}&lon={}&"
        "format=jsonv2&addressdetails=1&accept-language=en&zoom=18"
    ).format(latitude, longitude)

    requests_mock.get(expected_url, headers=header, json=location)
    actual_result = areas.query_location(latitude, longitude)

    actual_useragent = requests_mock.last_request.headers["User-Agent"]
    actual_url = requests_mock.last_request.url
    actual_timeout = requests_mock.last_request.timeout
    assert actual_useragent == expected_useragent
    assert actual_url == expected_url
    assert actual_result == location
    assert actual_timeout == 1


def test_init_database(mocker, connection):
    mocked_sqlite = mocker.patch("connord.areas.sqlite")

    areas.init_database(connection)

    mocked_sqlite.create_location_table.assert_called_once_with(connection)


def test_update_database_all_locations_exist(mocker, connection, servers):
    mocked_sqlite = mocker.patch("connord.areas.sqlite")
    mocked_sqlite.create_connection.return_value = connection
    mocked_sqlite.location_exists.return_value = True
    mocked_init = mocker.patch("connord.areas.init_database")
    mocked_query = mocker.patch("connord.areas.query_location")

    mocked_get_servers = mocker.patch(
        "connord.areas.servers.get_servers", return_value=servers
    )

    areas.update_database()

    mocked_sqlite.create_connection.assert_called()
    mocked_init.assert_called_once_with(connection)
    mocked_get_servers.assert_called_once()
    mocked_sqlite.location_exists.assert_called()
    mocked_query.assert_not_called()


def test_update_database_location_not_exists(
    mocker, location_json, connection, servers
):
    mocked_sqlite = mocker.patch("connord.areas.sqlite")
    mocked_sqlite.create_connection.return_value = connection
    mocked_sqlite.location_exists.side_effect = [
        False,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    ]
    mocked_init = mocker.patch("connord.areas.init_database")
    mocked_query = mocker.patch(
        "connord.areas.query_location", return_value=location_json
    )

    mocked_get_servers = mocker.patch(
        "connord.areas.servers.get_servers", return_value=servers
    )

    areas.update_database()

    mocked_sqlite.create_connection.assert_called()
    mocked_init.assert_called_once_with(connection)
    mocked_get_servers.assert_called_once()
    mocked_sqlite.location_exists.assert_called()
    mocked_query.assert_called()
    mocked_sqlite.create_location.assert_called_once()


def test_update_database_location_not_exists_when_city_is_unknown(
    # setup
    mocker,
    location_json,
    connection,
    servers,
):
    mocked_sqlite = mocker.patch("connord.areas.sqlite")
    mocked_sqlite.create_connection.return_value = connection
    mocked_sqlite.location_exists.side_effect = [
        False,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    ]
    mocked_init = mocker.patch("connord.areas.init_database")
    # delete keys
    location_json["address"].pop("city")
    location_json["address"].pop("state")

    mocked_query = mocker.patch(
        "connord.areas.query_location", return_value=location_json
    )

    mocked_get_servers = mocker.patch(
        "connord.areas.servers.get_servers", return_value=servers
    )

    # run
    areas.update_database()

    # assert
    mocked_sqlite.create_connection.assert_called()
    mocked_init.assert_called_once_with(connection)
    mocked_get_servers.assert_called_once()
    mocked_sqlite.location_exists.assert_called()
    mocked_query.assert_called()
    mocked_sqlite.create_location.assert_called_once()


def test_get_server_angulars(server):

    # setup
    expected_latitude = "40.123"
    expected_longitude = "50.321"

    # run
    actual_lat, actual_lon = areas.get_server_angulars(server)

    # assert
    assert expected_latitude == actual_lat
    assert expected_longitude == actual_lon


def test_verify_areas_when_areas_not_list():
    # run and assert
    try:
        areas.verify_areas(dict())
        assert False
    except TypeError as error:
        assert (
            str(error)
            == "Expected areas to be <class 'list'>: But found <class 'dict'>"
        )


def test_verify_areas_when_good(mocker, areas_good_fix, locations_db_fix):
    mocked_get_loc = mocker.patch(
        "connord.areas.get_locations", return_value=locations_db_fix
    )

    # run
    actual_areas = areas.verify_areas(areas_good_fix)

    # assert
    mocked_get_loc.assert_called_once()
    assert actual_areas == areas_good_fix


def test_verify_areas_when_area_ambiguous_found(mocker, locations_db_fix2):
    # setup
    mocked_get_loc = mocker.patch(
        "connord.areas.get_locations", return_value=locations_db_fix2
    )
    ambiguous_areas = ["mi", "min"]

    # run
    try:
        areas.verify_areas(ambiguous_areas)
        assert False
    except areas.AreaError as error:
        assert str(error) == (
            "Ambiguous Areas: mi: ['Minneapolis', 'Minnea'], min: "
            "['Minneapolis', 'Minnea']"
        )

    # assert
    mocked_get_loc.assert_called_once()


def test_verify_areas_when_area_not_found(mocker, areas_not_exist, locations_db_fix):
    # setup
    mocked_get_loc = mocker.patch(
        "connord.areas.get_locations", return_value=locations_db_fix
    )

    # run
    try:
        areas.verify_areas(areas_not_exist)
        assert False
    except ValueError as error:
        assert str(error) == ("Areas not found: {}".format(areas_not_exist))

    # assert
    mocked_get_loc.assert_called_once()


def test_get_translation_table():
    # setup
    expected_translation_table = {
        225: 97,
        227: 97,
        269: 99,
        235: 101,
        233: 101,
        351: 115,
        537: 115,
        357: 116,
    }

    # run
    actual_translation_table = areas.get_translation_table()

    # assert
    assert actual_translation_table == expected_translation_table


def test_filter_servers(mocker, servers, connection):
    # setup
    areas_ = ["fr"]
    cities = [
        "Frankfurt",
        "Frankfurt",
        "Frankfurt",
        "Amsterdam",
        "Amsterdam",
        "Amsteradm",
        "Manassas",
        "Dallas",
    ]
    expected_servers = get_expected_servers_by_domain(["de111", "de112", "de113"])
    mocked_sqlite = mocker.patch("connord.areas.sqlite")
    mocked_sqlite.create_connection.return_value = connection
    mocked_sqlite.location_exists.side_effect = [
        False,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    ]
    mocked_sqlite.get_city.side_effect = cities
    mocked_update = mocker.patch("connord.areas.update_database")

    # run
    actual_servers = areas.filter_servers(servers, areas_)

    # assert
    mocked_sqlite.create_connection.assert_called_once()
    mocked_sqlite.location_exists.assert_called()
    mocked_update.assert_called_once()

    assert actual_servers == expected_servers


def test_filter_servers_when_servers_is_none(areas_good_fix):
    # setup
    servers = None

    # run and assert
    try:
        areas.filter_servers(servers, areas_good_fix)
        assert False
    except TypeError as error:
        assert str(error) == "Servers may not be None"


def test_filter_servers_when_areas_is_none(servers):
    # run
    actual_servers = areas.filter_servers(servers, None)

    assert actual_servers == servers


def test_filter_servers_when_areas_is_empty(servers):
    # run
    actual_servers = areas.filter_servers(servers, list())

    assert actual_servers == servers


def test_filter_servers_when_servers_is_empty(areas_good_fix):
    # run
    actual_servers = areas.filter_servers(list(), areas_good_fix)

    assert actual_servers == list()


def test_get_min_id(mocker):
    # setup
    mocked_verify = mocker.patch("connord.areas.verify_areas")
    expected_id = "m"

    # run
    actual_id = areas.get_min_id("Minneapolis")

    # assert
    mocked_verify.assert_called_once_with([expected_id])
    assert actual_id == expected_id


def test_get_min_id_when_city_is_fully_ambiguous(mocker):
    # setup
    mocked_verify = mocker.patch("connord.areas.verify_areas")
    mocked_verify.side_effect = areas.AreaError
    expected_id = "minneapolis"

    # run
    actual_id = areas.get_min_id("Minneapolis")

    # assert
    mocked_verify.assert_called()
    assert actual_id == expected_id


def test_get_locations_when_locations_is_empty(mocker, connection, locations_db_fix):
    # setup
    mocked_sqlite = mocker.patch("connord.areas.sqlite")
    mocked_sqlite.create_connection.return_value = connection
    mocked_sqlite.get_locations.side_effect = [list(), locations_db_fix]
    mocked_update = mocker.patch("connord.areas.update_database")

    # run
    actual_locations = areas.get_locations()

    # assert
    mocked_sqlite.create_connection.assert_called_once()
    mocked_sqlite.get_locations.assert_called()
    mocked_update.assert_called_once()
    assert actual_locations == locations_db_fix


def test_get_locations_when_locations_is_not_empty(
    mocker, connection, locations_db_fix
):
    # setup
    mocked_sqlite = mocker.patch("connord.areas.sqlite")
    mocked_sqlite.create_connection.return_value = connection
    mocked_sqlite.get_locations.return_value = locations_db_fix
    mocked_update = mocker.patch("connord.areas.update_database")

    # run
    actual_locations = areas.get_locations()

    # assert
    mocked_sqlite.create_connection.assert_called_once()
    mocked_sqlite.get_locations.assert_called_once()
    mocked_update.assert_not_called()
    assert actual_locations == locations_db_fix


def test_area_pretty_formatter_format_headline(mocker):
    # setup
    expected_headline = """================================================================================
Mini ID :    Latitude        Longitude     City
Address
================================================================================"""
    formatter = areas.AreasPrettyFormatter()

    # run
    actual_headline = formatter.format_headline()

    # assert
    assert actual_headline == expected_headline


def test_area_pretty_formatter_format_area(mocker, locations_db_fix):
    # setup
    location = locations_db_fix[0]
    expected_output = """'min'   :   44.980000000°  -93.263611100°  Minneapolis                             
The Depot Renaissance Minneapolis Hotel, 3rd Avenue South, St Anthony West, Phillips, Minneapolis, Hennepin County, Minnesota, 55404, USA
--------------------------------------------------------------------------------"""
    formatter = areas.AreasPrettyFormatter()

    # run
    actual_output = formatter.format_area(location)

    # assert
    assert actual_output == expected_output


def test_to_string_when_stream_is_false(mocker, locations_db_output, locations_db_fix):
    mocked_locations = mocker.patch(
        "connord.areas.get_locations", return_value=locations_db_fix
    )

    # run
    actual_output = areas.to_string(stream=False)

    # assert
    mocked_locations.assert_called()
    assert actual_output == locations_db_output.rstrip()


def test_to_string_when_stream_is_true(
    capsys, mocker, locations_db_output, locations_db_fix
):
    mocked_locations = mocker.patch(
        "connord.areas.get_locations", return_value=locations_db_fix
    )

    # run
    actual_output = areas.to_string(stream=True)

    # assert
    mocked_locations.assert_called()
    captured = capsys.readouterr()
    assert actual_output == ""
    assert captured.out == locations_db_output
    assert captured.err == ""


def test_print_areas(mocker, capsys, locations_db_output, locations_db_fix):
    mocked_locations = mocker.patch(
        "connord.areas.get_locations", return_value=locations_db_fix
    )

    # run
    areas.print_areas()

    # assert
    mocked_locations.assert_called()
    captured = capsys.readouterr()
    assert captured.out == locations_db_output
    assert captured.err == ""
