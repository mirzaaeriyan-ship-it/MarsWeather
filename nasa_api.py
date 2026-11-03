
import requests

NASA_API_URL = (
    "https://mars.nasa.gov/rss/api/"
    "?feed=weather&category=msl&feedtype=json"
)


def get_mars_weather():

    response = requests.get(NASA_API_URL, timeout=20)
    response.raise_for_status()

    return response.json()


def get_records(data):

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in ("weather", "data", "results", "soles"):
        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            return list(value.values())

    sol_keys = data.get("sol_keys", [])

    if isinstance(sol_keys, list):
        return [
            data[sol]
            for sol in sol_keys
            if sol in data and isinstance(data[sol], dict)
        ]

    return [
        value for value in data.values()
        if isinstance(value, dict)
    ]


def get_value(record, possible_names):

    if not isinstance(record, dict):
        return None

    for name in possible_names:

        value = record.get(name)

        if isinstance(value, dict):

            value = (
                value.get("av")
                or value.get("average")
                or value.get("value")
            )

        if value is not None and value != "":
            return value

    return None


def get_latest_weather():

    data = get_mars_weather()
    records = get_records(data)

    if not records:
        return {
            "error": "No weather observations found."
        }

    record = records[-1]

    return {
        "observation_date": get_value(
            record,
            ["terrestrial_date", "date", "utc_date"]
        ),

        "sol": get_value(
            record,
            ["sol", "mars_sol"]
        ),

        "temperature": get_value(
            record,
            ["at", "air_temperature", "air_temp", "temperature"]
        ),

        "ground_temperature": get_value(
            record,
            ["ground_temperature", "ground_temp", "gts"]
        ),

        "wind_speed": get_value(
            record,
            ["wind_speed", "wind"]
        ),

        "pressure": get_value(
            record,
            ["pressure", "pressure_avg"]
        ),

        "raw_fields": list(record.keys())
    }
