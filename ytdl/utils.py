import requests


def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "AnRNicGadpqWZhntIcPHtRyNh-RLVUlurcE2UYWnxTpHdWMaHCed9lbG0HulN5WR"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print('data :')

    if data["status"] == "OK":
        results = data["results"]
        if len(results) > 0:
            location = results[0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return latitude, longitude

    return None, None


def get_hotels(location):
    latitude, longitude = geocode_address(location)

    if latitude is not None and longitude is not None:
        url = "https://dev.virtualearth.net/REST/v1/LocalSearch/"
        params = {
            "query": "hotels",
            "userLocation": f"{latitude},{longitude}",
            "key": "AnRNicGadpqWZhntIcPHtRyNh-RLVUlurcE2UYWnxTpHdWMaHCed9lbG0HulN5WR"
        }
        response = requests.get(url, params=params)
        data = response.json()
        print(data)

        hotels = []
        if "resourceSets" in data and len(data["resourceSets"]) > 0:
            resources = data["resourceSets"][0]["resources"]
            for resource in resources:
                hotel_name = resource["name"]
                hotel_address = resource["address"]["formattedAddress"]
                hotel_latitude = resource["point"]["coordinates"][0]
                hotel_longitude = resource["point"]["coordinates"][1]
                hotels.append({"name": hotel_name, "address": hotel_address, "latitude": hotel_latitude,
                               "longitude": hotel_longitude})

        return hotels

    return []

