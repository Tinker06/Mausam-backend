"""
MAUSAM — Personalization Engine
Owner: Person 4

This file takes (persona + weather data) and returns a personalized
recommendation, following the contract in personalization_contract.md.

Timeline of what was added when:
Sept 19 - skeleton + dispatcher
Sept 20 - Health persona logic
Sept 21 - Fitness persona logic
Sept 22 - Beach persona logic
Sept 23 - Traveler persona logic
Sept 24 - 9 universal occupation messages
Sept 25 - Foreigner climate comparison
Sept 26 - All messages centralized behind translation keys (see MESSAGE_TEMPLATES)
Sept 27 - Official severe-weather warnings now override/boost persona output
Sept 28 - Integration test matrix (persona x weather condition)
Sept 29 - Edge-case hardening (missing/garbage input never crashes)
"""

from typing import Optional


# ---------------------------------------------------------------------------
# SEPT 26: Centralized message templates.
# Every user-facing sentence lives HERE, keyed by a short id, instead of
# being written directly inside each persona function. This is what
# "routes through localization keys" means in practice: Person 6's
# frontend translation files (en.json/ta.json/hi.json) will eventually
# use these SAME keys to show Tamil/Hindi text instead of English -- the
# persona logic below never needs to change when that happens.
# ---------------------------------------------------------------------------

MESSAGE_TEMPLATES = {
    # Health
    "health.aqi.hazardous": "Air quality is hazardous today — avoid outdoor activity if possible.",
    "health.aqi.very_unhealthy": "Air quality is very unhealthy — people with asthma or allergies should stay indoors.",
    "health.aqi.poor": "Air quality is poor — consider limiting prolonged outdoor exertion.",
    "health.aqi.moderate": "Air quality is moderate — sensitive groups should take care outdoors.",
    "health.uv.extreme": "UV index is extreme — avoid sun exposure between 10 AM and 4 PM.",
    "health.uv.very_high": "UV index is very high — wear sunscreen and sunglasses outdoors.",
    "health.uv.high": "UV index is high — sun protection is recommended.",
    "health.humidity.high": "High humidity today — it may feel more uncomfortable than the temperature suggests.",
    "health.pollen.high": "Pollen levels are high — allergy sufferers should take precautions.",
    "health.pollen.moderate": "Pollen levels are moderate — mild allergy symptoms are possible.",
    "health.all_clear": "Air quality, UV, humidity and pollen levels look fine today.",

    # Fitness
    "fitness.heat.extreme": "Very hot conditions — avoid outdoor exercise between 10 AM and 4 PM.",
    "fitness.heat.warm": "Warm conditions — exercise earlier in the day if possible.",
    "fitness.wind.strong": "Strong winds today — outdoor running conditions may be difficult.",
    "fitness.rain.high_chance": "High chance of rain — consider an indoor workout today.",
    "fitness.all_clear": "Good conditions for outdoor activity — best window is {best_hours}.",

    # Beach
    "beach.wave.unsafe": "Wave heights are unsafe for swimming today — avoid the water.",
    "beach.wave.moderate": "Moderate waves today — swim with caution and stay near lifeguards.",
    "beach.wind.strong": "Strong winds are affecting sea conditions — check local advisories.",
    "beach.water.cool": "Water is on the cooler side today — a wetsuit is recommended.",
    "beach.all_clear": "Sea conditions look good for a beach day.",

    # Traveler
    "traveler.warmer": "Your destination is considerably warmer than here.",
    "traveler.cooler": "Your destination is considerably cooler than here.",
    "traveler.similar": "Your destination's temperature is fairly similar to here.",
    "traveler.rain_tip": "Carry a raincoat or umbrella — rain is expected at your destination.",
    "traveler.missing_data": "Add your destination to see a packing suggestion.",

    # Foreigner
    "foreigner.warmer": "India today is considerably warmer than {country}.",
    "foreigner.cooler": "India today is considerably cooler than {country}.",
    "foreigner.similar": "India today is fairly similar in temperature to {country}.",
    "foreigner.rain_tip": "Rain is likely — carry rain protection.",
    "foreigner.unknown_country": "Select your home country to see a climate comparison.",

    # Shared / official warnings (Sept 27)
    "official_warning.prefix": "Official weather warning: {warning_message}",

    # Fallback
    "fallback.unknown_persona": "Personalized recommendations for this persona are coming soon.",
    "fallback.error": "We couldn't generate a personalized update right now — showing general info instead.",
}


def _translate(key: str, language: str = "en", **params) -> str:
    """
    Looks up a message by its key instead of hardcoding English text
    inline. Right now this only has English templates -- Person 6 extends
    this on the frontend with i18next for Tamil/Hindi, using these exact
    same keys. The persona logic never needs to change when that happens.
    """
    template = MESSAGE_TEMPLATES.get(key, "Information not available.")
    try:
        return template.format(**params)
    except (KeyError, IndexError):
        return template


# ---------------------------------------------------------------------------
# STEP 1: The dispatcher — the ONLY function other teammates call directly.
# ---------------------------------------------------------------------------

def personalize(persona: str, weather: dict, language: str = "en",
                 home_country: Optional[str] = None) -> dict:
    """
    Main entry point. Person 1 (tech lead) calls this function from FastAPI.

    Sept 29 hardening: this function NEVER raises an exception. If
    anything inside goes wrong (bad persona, malformed weather data,
    weather being None instead of a dict, etc.), it returns a safe
    fallback response instead of crashing the whole API request.
    """
    try:
        # Defensive default: never let a missing/None weather object crash us.
        if not isinstance(weather, dict):
            weather = {}

        persona_handlers = {
            "health": _handle_health,
            "fitness": _handle_fitness,
            "beach": _handle_beach,
            "traveler": _handle_traveler,
        }

        handler = persona_handlers.get(persona)

        if handler is not None:
            output = handler(weather)
        elif persona == "foreigner":
            output = _handle_foreigner(weather, home_country)
        elif persona in OCCUPATION_MESSAGES:
            output = _handle_occupation(persona, weather)
        else:
            output = _fallback_response(persona)

        # Sept 27: apply any official severe-weather warning on top of
        # whatever the persona logic decided, regardless of which persona.
        output = _apply_official_warning(output, weather)

        return output

    except Exception:
        # Sept 29: absolute last-resort safety net. Something unexpected
        # went wrong above -- never let the API call fail because of it.
        return _build_output(
            persona=str(persona),
            headline="MAUSAM",
            message_key="fallback.error",
            message=_translate("fallback.error"),
            priority="low",
            cards=[],
        )


# ---------------------------------------------------------------------------
# SEPT 20: Health persona
# ---------------------------------------------------------------------------

def _handle_health(weather: dict) -> dict:
    aqi = weather.get("aqi")
    uv_index = weather.get("uv_index")
    humidity = weather.get("humidity")
    pollen_level = weather.get("pollen_level")

    cards = []
    warnings = []  # list of (severity_rank, message_key, params_dict)

    if isinstance(aqi, (int, float)):
        cards.append({"type": "aqi", "value": aqi})
        if aqi > 200:
            warnings.append((3, "health.aqi.hazardous", {}))
        elif aqi > 150:
            warnings.append((3, "health.aqi.very_unhealthy", {}))
        elif aqi > 100:
            warnings.append((2, "health.aqi.poor", {}))
        elif aqi > 50:
            warnings.append((1, "health.aqi.moderate", {}))

    if isinstance(uv_index, (int, float)):
        cards.append({"type": "uv", "value": uv_index})
        if uv_index >= 11:
            warnings.append((3, "health.uv.extreme", {}))
        elif uv_index >= 8:
            warnings.append((2, "health.uv.very_high", {}))
        elif uv_index >= 6:
            warnings.append((1, "health.uv.high", {}))

    if isinstance(humidity, (int, float)):
        cards.append({"type": "humidity", "value": humidity})
        if humidity >= 80:
            warnings.append((1, "health.humidity.high", {}))

    if pollen_level is not None:
        cards.append({"type": "pollen", "value": pollen_level})
        if pollen_level == "high":
            warnings.append((2, "health.pollen.high", {}))
        elif pollen_level == "moderate":
            warnings.append((1, "health.pollen.moderate", {}))

    if warnings:
        warnings.sort(key=lambda w: w[0], reverse=True)
        top_rank, top_key, top_params = warnings[0]
        priority = {3: "high", 2: "medium", 1: "low"}[top_rank]
        message_key = top_key
        message = _translate(top_key, **top_params)
        headline = "Health alert for today" if top_rank >= 2 else "Health check for today"
    else:
        priority = "low"
        message_key = "health.all_clear"
        message = _translate(message_key)
        headline = "All clear today"

    return _build_output("health", headline, message_key, message, priority, cards)


# ---------------------------------------------------------------------------
# SEPT 21: Fitness persona
# ---------------------------------------------------------------------------

def _handle_fitness(weather: dict) -> dict:
    temperature = weather.get("temperature")
    wind_speed = weather.get("wind_speed")
    rain_probability = weather.get("rain_probability")
    sunrise = weather.get("sunrise")

    cards = []
    warnings = []

    best_hours = f"{sunrise} onward (next 2 hours are coolest)" if sunrise else "6:00 AM – 8:00 AM"
    cards.append({"type": "best_running_hours", "value": best_hours})

    if isinstance(temperature, (int, float)):
        cards.append({"type": "temperature", "value": temperature})
        if temperature > 35:
            warnings.append((3, "fitness.heat.extreme", {}))
        elif temperature > 30:
            warnings.append((2, "fitness.heat.warm", {}))

    if isinstance(wind_speed, (int, float)):
        cards.append({"type": "wind", "value": wind_speed})
        if wind_speed > 30:
            warnings.append((2, "fitness.wind.strong", {}))

    if isinstance(rain_probability, (int, float)):
        cards.append({"type": "rain_probability", "value": rain_probability})
        if rain_probability > 60:
            warnings.append((2, "fitness.rain.high_chance", {}))

    if warnings:
        warnings.sort(key=lambda w: w[0], reverse=True)
        top_rank, top_key, top_params = warnings[0]
        priority = {3: "high", 2: "medium", 1: "low"}[top_rank]
        message_key = top_key
        message = _translate(top_key, **top_params)
        headline = "Heads up before your workout" if top_rank >= 2 else "Good day for a workout"
    else:
        priority = "low"
        message_key = "fitness.all_clear"
        message = _translate(message_key, best_hours=best_hours)
        headline = "Good day for a workout"

    return _build_output("fitness", headline, message_key, message, priority, cards)


# ---------------------------------------------------------------------------
# SEPT 22: Beach persona
# ---------------------------------------------------------------------------

def _handle_beach(weather: dict) -> dict:
    tide = weather.get("tide")
    wave_height_m = weather.get("wave_height_m")
    water_temperature = weather.get("water_temperature")
    wind_speed = weather.get("wind_speed")

    cards = []
    warnings = []

    if isinstance(wave_height_m, (int, float)):
        cards.append({"type": "wave_height", "value": wave_height_m})
        if wave_height_m > 2.5:
            warnings.append((3, "beach.wave.unsafe", {}))
        elif wave_height_m > 1.5:
            warnings.append((2, "beach.wave.moderate", {}))

    if isinstance(wind_speed, (int, float)):
        cards.append({"type": "wind", "value": wind_speed})
        if wind_speed > 25:
            warnings.append((2, "beach.wind.strong", {}))

    if isinstance(water_temperature, (int, float)):
        cards.append({"type": "water_temperature", "value": water_temperature})
        if water_temperature < 20:
            warnings.append((1, "beach.water.cool", {}))

    if tide is not None:
        cards.append({"type": "tide", "value": tide})

    if warnings:
        warnings.sort(key=lambda w: w[0], reverse=True)
        top_rank, top_key, top_params = warnings[0]
        priority = {3: "high", 2: "medium", 1: "low"}[top_rank]
        message_key = top_key
        message = _translate(top_key, **top_params)
        headline = "Check before you go in" if top_rank >= 2 else "Beach conditions today"
    else:
        priority = "low"
        message_key = "beach.all_clear"
        message = _translate(message_key)
        headline = "Great beach day"

    return _build_output("beach", headline, message_key, message, priority, cards)


# ---------------------------------------------------------------------------
# SEPT 23: Traveler persona
# ---------------------------------------------------------------------------

def _handle_traveler(weather: dict) -> dict:
    home_temp = weather.get("temperature")
    destination_temp = weather.get("destination_temperature")
    destination_condition = weather.get("destination_condition") or ""

    cards = []
    if isinstance(home_temp, (int, float)):
        cards.append({"type": "home_temperature", "value": home_temp})
    if isinstance(destination_temp, (int, float)):
        cards.append({"type": "destination_temperature", "value": destination_temp})

    if not isinstance(home_temp, (int, float)) or not isinstance(destination_temp, (int, float)):
        message_key = "traveler.missing_data"
        return _build_output("traveler", "Travel weather", message_key,
                              _translate(message_key), "low", cards)

    diff = destination_temp - home_temp
    cards.append({"type": "temperature_difference", "value": diff})

    if diff >= 8:
        message_key = "traveler.warmer"
    elif diff <= -8:
        message_key = "traveler.cooler"
    else:
        message_key = "traveler.similar"

    message = _translate(message_key)
    priority = "medium" if abs(diff) >= 8 else "low"

    if "rain" in destination_condition.lower():
        cards.append({"type": "packing_tip", "value": _translate("traveler.rain_tip")})
        priority = "medium"

    return _build_output("traveler", "Before you pack", message_key, message, priority, cards)


# ---------------------------------------------------------------------------
# SEPT 24: Universal occupation messages
# ---------------------------------------------------------------------------

OCCUPATION_MESSAGES = {
    "fisherman": {
        "low": "Sea and wind conditions look manageable for a fishing trip today.",
        "medium": "Wind conditions are picking up — check marine warnings before heading out.",
        "high": "Strong winds and rain expected — fishing trips are not advised today.",
    },
    "vendor": {
        "low": "Comfortable selling conditions expected today.",
        "medium": "Hot afternoon expected — keep more chilled drinks and water available.",
        "high": "Heavy rain expected — plan for reduced foot traffic and cover your stall.",
    },
    "delivery_worker": {
        "low": "Clear conditions for deliveries today.",
        "medium": "Rain possible later — plan your route and carry rain gear.",
        "high": "Heavy rain and reduced visibility expected — allow extra time for deliveries.",
    },
    "gardener": {
        "low": "Good conditions for regular garden care today.",
        "medium": "Rain expected later — you may be able to skip watering today.",
        "high": "Heavy rain expected — hold off on watering and check drainage.",
    },
    "student": {
        "low": "Pleasant conditions for your commute today.",
        "medium": "Rain possible — carry an umbrella for your commute.",
        "high": "Heavy rain expected — plan extra travel time and stay safe.",
    },
    "tourist": {
        "low": "Great conditions for sightseeing today.",
        "medium": "Some rain possible — keep an indoor backup plan handy.",
        "high": "Heavy rain expected — consider indoor attractions today.",
    },
    "sports_person": {
        "low": "Good conditions for outdoor practice today.",
        "medium": "Hot or windy conditions — consider adjusting practice timing or intensity.",
        "high": "Poor conditions for outdoor practice — consider moving training indoors.",
    },
    "it_professional": {
        "low": "No weather concerns for your commute today.",
        "medium": "Rain expected during typical commute hours — consider leaving earlier.",
        "high": "Heavy rain or storm expected — consider working from home if possible.",
    },
    "homemaker": {
        "low": "Good drying weather today.",
        "medium": "Humid conditions — clothes may take longer to dry.",
        "high": "Rain expected — plan for indoor drying today.",
    },
}


def _compute_generic_risk(weather: dict) -> str:
    rain_probability = weather.get("rain_probability") or 0
    wind_speed = weather.get("wind_speed") or 0
    if not isinstance(rain_probability, (int, float)):
        rain_probability = 0
    if not isinstance(wind_speed, (int, float)):
        wind_speed = 0

    if rain_probability >= 60 or wind_speed >= 30:
        return "high"
    elif rain_probability >= 30 or wind_speed >= 18:
        return "medium"
    else:
        return "low"


def _handle_occupation(persona: str, weather: dict) -> dict:
    risk = _compute_generic_risk(weather)
    messages = OCCUPATION_MESSAGES.get(persona)
    if messages is None:
        return _fallback_response(persona)

    headline = f"Today's update for {persona.replace('_', ' ').title()}"
    cards = [
        {"type": "rain_probability", "value": weather.get("rain_probability")},
        {"type": "wind", "value": weather.get("wind_speed")},
    ]
    message_key = f"personalization.occupation.{persona}.{risk}"

    return _build_output(persona, headline, message_key, messages[risk], risk, cards)


# ---------------------------------------------------------------------------
# SEPT 25: Foreigner climate comparison
# ---------------------------------------------------------------------------

COUNTRY_CLIMATE_PROFILES = {
    "uk": {"name": "United Kingdom", "avg_temperature": 12},
    "usa": {"name": "United States", "avg_temperature": 15},
    "canada": {"name": "Canada", "avg_temperature": 8},
    "japan": {"name": "Japan", "avg_temperature": 16},
    "australia": {"name": "Australia", "avg_temperature": 20},
}


def _handle_foreigner(weather: dict, home_country: Optional[str]) -> dict:
    india_temp = weather.get("temperature")
    profile = COUNTRY_CLIMATE_PROFILES.get(home_country) if home_country else None

    if profile is None or not isinstance(india_temp, (int, float)):
        message_key = "foreigner.unknown_country"
        return _build_output("foreigner", "Visiting India?", message_key,
                              _translate(message_key), "low", [])

    diff = india_temp - profile["avg_temperature"]
    cards = [{"type": "india_temperature", "value": india_temp}]

    if diff >= 8:
        message_key = "foreigner.warmer"
    elif diff <= -8:
        message_key = "foreigner.cooler"
    else:
        message_key = "foreigner.similar"

    message = _translate(message_key, country=profile["name"])
    priority = "medium" if abs(diff) >= 8 else "low"

    rain_probability = weather.get("rain_probability") or 0
    if isinstance(rain_probability, (int, float)) and rain_probability >= 40:
        cards.append({"type": "tip", "value": _translate("foreigner.rain_tip")})
        priority = "medium"

    headline = f"Visiting from {profile['name']}?"
    return _build_output("foreigner", headline, message_key, message, priority, cards)


# ---------------------------------------------------------------------------
# SEPT 27: Official severe-weather warning override.
# Person 3 (weather backend) / Person 5 (alerts) will attach an optional
# "warning" object to the weather payload when IMD/district data flags a
# real alert, shaped like:
#   weather["warning"] = {"severity": "severe", "message": "Heavy rain warning issued"}
# When present, we add it as a prominent card on TOP of whatever the
# persona logic already decided, and raise priority if it's serious.
# ---------------------------------------------------------------------------

def _apply_official_warning(output: dict, weather: dict) -> dict:
    warning = weather.get("warning")
    if not isinstance(warning, dict):
        return output  # nothing to do, most of the time

    severity = str(warning.get("severity", "")).lower()
    warning_message = warning.get("message", "")

    if not warning_message:
        return output

    output["cards"].insert(0, {
        "type": "official_warning",
        "value": _translate("official_warning.prefix", warning_message=warning_message),
    })

    if severity in ("severe", "extreme", "high"):
        output["priority"] = "high"

    return output


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_output(persona: str, headline: str, message_key: str,
                   message: str, priority: str, cards: list) -> dict:
    return {
        "persona": persona,
        "headline": headline,
        "message_key": message_key,
        "message": message,
        "priority": priority,
        "cards": cards,
    }


def _fallback_response(persona: str) -> dict:
    message_key = "fallback.unknown_persona"
    return _build_output(persona, "Welcome to MAUSAM", message_key,
                          _translate(message_key), "low", [])


# ---------------------------------------------------------------------------
# SEPT 28: INTEGRATION DAY — persona x weather-condition test matrix.
# Not a new feature; this just runs every persona against several
# realistic weather situations to catch anything broken before merging.
# ---------------------------------------------------------------------------

def _run_integration_matrix():
    print("\n\n========== SEPT 28: INTEGRATION TEST MATRIX ==========")

    weather_conditions = {
        "calm": {"temperature": 26, "humidity": 55, "wind_speed": 8, "rain_probability": 10,
                  "uv_index": 4, "aqi": 40, "pollen_level": "low",
                  "tide": "low", "wave_height_m": 0.8, "water_temperature": 27,
                  "destination_temperature": 24, "destination_condition": "Clear"},
        "moderate": {"temperature": 32, "humidity": 70, "wind_speed": 20, "rain_probability": 40,
                     "uv_index": 7, "aqi": 110, "pollen_level": "moderate",
                     "tide": "rising", "wave_height_m": 1.8, "water_temperature": 24,
                     "destination_temperature": 14, "destination_condition": "Cloudy"},
        "severe": {"temperature": 38, "humidity": 90, "wind_speed": 35, "rain_probability": 80,
                   "uv_index": 12, "aqi": 260, "pollen_level": "high",
                   "tide": "high", "wave_height_m": 3.0, "water_temperature": 18,
                   "destination_temperature": 5, "destination_condition": "Heavy Rain",
                   "warning": {"severity": "severe", "message": "Heavy rain warning issued for your district"}},
    }

    core_personas = ["health", "fitness", "beach", "traveler"]
    occupations = list(OCCUPATION_MESSAGES.keys())
    all_personas = core_personas + occupations + ["foreigner", "not_a_real_persona"]

    failures = []

    for condition_name, weather in weather_conditions.items():
        for persona in all_personas:
            result = personalize(persona, weather, home_country="uk")
            required_fields = {"persona", "headline", "message_key", "message", "priority", "cards"}
            if not required_fields.issubset(result.keys()):
                failures.append((condition_name, persona, "missing fields"))
            if result["priority"] not in ("low", "medium", "high"):
                failures.append((condition_name, persona, "bad priority value"))

    print(f"Ran {len(weather_conditions) * len(all_personas)} persona x condition combinations.")
    if failures:
        print(f"FAILURES FOUND: {failures}")
    else:
        print("All combinations returned valid, correctly-shaped output. No failures.")


# ---------------------------------------------------------------------------
# SEPT 29: Edge-case / malformed-input testing.
# ---------------------------------------------------------------------------

def _run_edge_case_tests():
    print("\n\n========== SEPT 29: EDGE CASE TESTS ==========")

    edge_cases = [
        ("weather is None", None),
        ("weather is empty dict", {}),
        ("weather is a string (malformed)", "not a real weather object"),
        ("weather has wrong types", {"temperature": "very hot", "wind_speed": None}),
        ("negative/extreme values", {"temperature": -50, "wind_speed": 999, "aqi": -10, "uv_index": 100}),
    ]

    for label, bad_weather in edge_cases:
        print(f"\n--- Edge case: {label} ---")
        try:
            result = personalize("health", bad_weather)
            print(f"OK — no crash. priority={result['priority']}, message={result['message']}")
        except Exception as e:
            print(f"FAILED — this should never happen: {e}")

    # Also test a completely invalid persona
    print("\n--- Edge case: completely invalid persona name ---")
    result = personalize("xyz_not_real", {"temperature": 30})
    print(f"OK — no crash. Returned fallback: {result}")


# ---------------------------------------------------------------------------
# Manual test runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Basic pipeline test (core personas) ===")
    sample_weather = {"temperature": 31, "humidity": 76, "wind_speed": 14, "uv_index": 8}
    for test_persona in ["health", "fitness", "beach", "traveler", "unknown_persona"]:
        print(f"\n--- {test_persona} ---")
        print(personalize(test_persona, sample_weather))

    print("\n\n=== Sept 27: Official warning override test ===")
    weather_with_warning = {
        "temperature": 29, "humidity": 60, "wind_speed": 10,
        "warning": {"severity": "severe", "message": "Heavy rain warning issued for your district"},
    }
    print(personalize("fitness", weather_with_warning))

    _run_integration_matrix()   # Sept 28
    _run_edge_case_tests()      # Sept 29
