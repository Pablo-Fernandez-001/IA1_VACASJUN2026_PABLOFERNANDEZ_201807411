def normalize_atom(value):
    return str(value)


def normalize_route(route):
    return [normalize_atom(city) for city in route]


def normalize_routes(routes):
    normalized = []

    for item in routes:
        distance = item[0]
        route = normalize_route(item[1])

        normalized.append({
            "distancia": distance,
            "ruta": route
        })

    return normalized