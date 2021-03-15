from . import Filters

FILTER = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "enum": list(map(str, Filters)),
        },
        "params": {
            "type": "object",
            "properties": dict(),
        }
    }
}

FILTERS_DATA = {
    "type": "array",
    "items": FILTER,
}
