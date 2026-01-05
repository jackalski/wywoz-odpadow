"""Constants for the Wywóz Odpadów integration."""

DOMAIN = "wywoz_odpadow"

# API Configuration
API_BASE_URL = "https://warszawa19115.pl/harmonogramy-wywozu-odpadow"
API_RESOURCE_ID = "ajaxResource"
API_AUTOCOMPLETE_RESOURCE_ID = "autocompleteResource"
API_PARAMS = {
    "p_p_id": "portalCKMjunkschedules_WAR_portalCKMjunkschedulesportlet_INSTANCE_o5AIb2mimbRJ",
    "p_p_lifecycle": "2",
    "p_p_state": "normal",
    "p_p_mode": "view",
    "p_p_resource_id": API_RESOURCE_ID,
    "p_p_cacheability": "cacheLevelPage",
}
API_AUTOCOMPLETE_PARAMS = {
    "p_p_id": "portalCKMjunkschedules_WAR_portalCKMjunkschedulesportlet_INSTANCE_o5AIb2mimbRJ",
    "p_p_lifecycle": "2",
    "p_p_state": "normal",
    "p_p_mode": "view",
    "p_p_resource_id": API_AUTOCOMPLETE_RESOURCE_ID,
    "p_p_cacheability": "cacheLevelPage",
}

# Default update interval (1 day in days for UI, kept in seconds for internal use)
DEFAULT_UPDATE_INTERVAL_DAYS = 1
# Keep old constant for backward compatibility (24 hours in seconds)
DEFAULT_UPDATE_INTERVAL = 86400

# Configuration keys
CONF_ADDRESS_POINT_ID = "address_point_id"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_POSTAL_CODE = "postal_code"

# Fraction type mappings for TrashCard compatibility
FRACTION_TYPE_MAPPING = {
    "zmieszane odpady opakowaniowe": "waste",
    "niesegregowane (zmieszane) odpady komunalne": "waste",
    "opakowania z papieru i tektury": "paper",
    "opakowania ze szkła": "recycle",
    "odpady ulegające biodegradacji": "organic",
    "odpady kuchenne ulegające biodegradacji": "organic",
    "odpady wielkogabarytowe": "others",
}

