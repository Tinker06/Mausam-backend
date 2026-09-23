"""
MAUSAM — Personalization Engine
Owner: Person 4
Started: Sept 19 (skeleton). Real logic added Sept 20-27.

This file takes (persona + weather data) and returns a personalized
recommendation, following the contract in personalization_contract.md.
"""

from typing import Optional


# ---------------------------------------------------------------------------
# STEP 1: The "dispatcher" — this is the ONLY function other teammates call.
# It looks at which persona was requested and routes to the right function.
# Everything else in this file is a private helper.
# ---------------------------------------------------------------------------

def personalize(persona: str, weather: dict, language: str = "en",
                 home_country: Optional[str] = None) -> dict:
    """
    Main entry point. Person 1 (tech lead) calls this function from FastAPI.

    Args:
        persona: "health", "fitness", "beach", "traveler", "foreigner",
                  or an occupation key like "fisherman" / "vendor" / etc.
                  (see OCCUPATION_MESSAGES for the full occupation list)
        weather: a dict matching the weather fields in the contract
                  (temperature, humidity, uv_index, etc.) — some fields
                  may be missing/None, always check before using them
        language: "en" / "ta" / "hi" — not used yet, added Sept 26
        home_country: only used when persona == "foreigner", e.g. "uk"

    Returns:
        A dict matching the OUTPUT contract: headline, message_key,
        message, priority, cards.
    """

    # This dictionary maps the 4 CORE personas to their dedicated function.
    # To add a new core persona later, add one line here.
    persona_handlers = {
        "health": _handle_health,
        "fitness": _handle_fitness,
        "beach": _handle_beach,
        "traveler": _handle_traveler,
    }

    handler = persona_handlers.get(persona)
    if handler is not None:
        return handler(weather)

    # Foreigner comparison has its own function since it needs an extra
    # argument (home_country) that the other personas don't use.
    if persona == "foreigner":
        return _handle_foreigner(weather, home_country)

    # Any occupation name (fisherman, vendor, etc.) goes through the
    # shared generic occupation handler.
    if persona in OCCUPATION_MESSAGES:
        return _handle_occupation(persona, weather)

    # Unknown persona — never crash, always return something safe.
    return _fallback_response(persona)


# ---------------------------------------------------------------------------
# STEP 2: One placeholder function per persona.
# Today (Sept 19) these just return dummy-but-valid output so we can test
# the pipeline end-to-end. Real logic replaces the "TODO" lines on their
# scheduled day.
# ---------------------------------------------------------------------------

def _handle_health(weather: dict) -> dict:
    """
    Sept 20: Real logic for the Health persona.

    Checks 4 things: AQI, UV index, humidity, pollen level.
    Each check that finds a concern adds a (severity_rank, message) pair
    to `warnings`. Rank 3 = most urgent, 1 = mild. At the end we pick the
    SINGLE most urgent warning as the main headline/message, but every
    value we checked still shows up as a small card regardless of severity.
    """

    aqi = weather.get("aqi")
    uv_index = weather.get("uv_index")
    humidity = weather.get("humidity")
    pollen_level = weather.get("pollen_level")  # expected: "low"/"moderate"/"high"

    cards = []
    warnings = []  # list of (severity_rank, message_text)

    # --- Check 1: Air Quality Index (AQI) ---
    # Standard AQI bands: 0-50 Good, 51-100 Moderate, 101-150 Poor,
    # 151-200 Very Unhealthy, 200+ Hazardous.
    if aqi is not None:
        cards.append({"type": "aqi", "value": aqi})
        if aqi > 200:
            warnings.append((3, "Air quality is hazardous today — avoid outdoor activity if possible."))
        elif aqi > 150:
            warnings.append((3, "Air quality is very unhealthy — people with asthma or allergies should stay indoors."))
        elif aqi > 100:
            warnings.append((2, "Air quality is poor — consider limiting prolonged outdoor exertion."))
        elif aqi > 50:
            warnings.append((1, "Air quality is moderate — sensitive groups should take care outdoors."))

    # --- Check 2: UV Index ---
    # 0-2 Low, 3-5 Moderate, 6-7 High, 8-10 Very High, 11+ Extreme.
    if uv_index is not None:
        cards.append({"type": "uv", "value": uv_index})
        if uv_index >= 11:
            warnings.append((3, "UV index is extreme — avoid sun exposure between 10 AM and 4 PM."))
        elif uv_index >= 8:
            warnings.append((2, "UV index is very high — wear sunscreen and sunglasses outdoors."))
        elif uv_index >= 6:
            warnings.append((1, "UV index is high — sun protection is recommended."))

    # --- Check 3: Humidity ---
    # High humidity makes conditions feel worse even if temperature is normal.
    if humidity is not None:
        cards.append({"type": "humidity", "value": humidity})
        if humidity >= 80:
            warnings.append((1, "High humidity today — it may feel more uncomfortable than the temperature suggests."))

    # --- Check 4: Pollen level ---
    if pollen_level is not None:
        cards.append({"type": "pollen", "value": pollen_level})
        if pollen_level == "high":
            warnings.append((2, "Pollen levels are high — allergy sufferers should take precautions."))
        elif pollen_level == "moderate":
            warnings.append((1, "Pollen levels are moderate — mild allergy symptoms are possible."))

    # --- Pick the single most urgent warning to be the headline message ---
    if warnings:
        # Sort so the highest severity_rank comes first, then take that one.
        warnings.sort(key=lambda w: w[0], reverse=True)
        top_rank, top_message = warnings[0]
        priority_map = {3: "high", 2: "medium", 1: "low"}
        priority = priority_map[top_rank]
        message = top_message
        headline = "Health alert for today" if top_rank >= 2 else "Health check for today"
    else:
        # Nothing concerning found (or no data available at all) — safe default.
        priority = "low"
        message = "Air quality, UV, humidity and pollen levels look fine today."
        headline = "All clear today"

    return _build_output(
        persona="health",
        headline=headline,
        message_key="personalization.health.auto_generated",  # replaced with granular keys on Sept 26
        message=message,
        priority=priority,
        cards=cards,
    )


def _handle_fitness(weather: dict) -> dict:
    """
    Sept 21: Real logic for the Fitness persona.

    Checks: best running window (based on sunrise), temperature-based heat
    warning, wind speed, and rain probability. Same "collect warnings, pick
    the most urgent" pattern as Health.
    """

    temperature = weather.get("temperature")
    wind_speed = weather.get("wind_speed")
    rain_probability = weather.get("rain_probability")
    sunrise = weather.get("sunrise")

    cards = []
    warnings = []

    # --- Best running hours ---
    # We don't have hour-by-hour forecast data yet, so we approximate:
    # the 2 hours right after sunrise are usually coolest. If sunrise
    # isn't available, fall back to a generic early-morning window.
    if sunrise is not None:
        best_hours = f"{sunrise} onward (next 2 hours are coolest)"
    else:
        best_hours = "6:00 AM – 8:00 AM"
    cards.append({"type": "best_running_hours", "value": best_hours})

    # --- Heat check ---
    if temperature is not None:
        cards.append({"type": "temperature", "value": temperature})
        if temperature > 35:
            warnings.append((3, "Very hot conditions — avoid outdoor exercise between 10 AM and 4 PM."))
        elif temperature > 30:
            warnings.append((2, "Warm conditions — exercise earlier in the day if possible."))

    # --- Wind check ---
    if wind_speed is not None:
        cards.append({"type": "wind", "value": wind_speed})
        if wind_speed > 30:
            warnings.append((2, "Strong winds today — outdoor running conditions may be difficult."))

    # --- Rain check ---
    if rain_probability is not None:
        cards.append({"type": "rain_probability", "value": rain_probability})
        if rain_probability > 60:
            warnings.append((2, "High chance of rain — consider an indoor workout today."))

    if warnings:
        warnings.sort(key=lambda w: w[0], reverse=True)
        top_rank, top_message = warnings[0]
        priority_map = {3: "high", 2: "medium", 1: "low"}
        priority = priority_map[top_rank]
        message = top_message
        headline = "Heads up before your workout" if top_rank >= 2 else "Good day for a workout"
    else:
        priority = "low"
        message = f"Good conditions for outdoor activity — best window is {best_hours}."
        headline = "Good day for a workout"

    return _build_output(
        persona="fitness",
        headline=headline,
        message_key="personalization.fitness.auto_generated",
        message=message,
        priority=priority,
        cards=cards,
    )


def _handle_beach(weather: dict) -> dict:
    """
    Sept 22: Real logic for the Beach/Surfer persona.

    Checks: wave height (safety), wind speed (sea conditions), water
    temperature (comfort), and tide (informational).
    """

    tide = weather.get("tide")
    wave_height_m = weather.get("wave_height_m")
    water_temperature = weather.get("water_temperature")
    wind_speed = weather.get("wind_speed")

    cards = []
    warnings = []

    # --- Wave height check ---
    if wave_height_m is not None:
        cards.append({"type": "wave_height", "value": wave_height_m})
        if wave_height_m > 2.5:
            warnings.append((3, "Wave heights are unsafe for swimming today — avoid the water."))
        elif wave_height_m > 1.5:
            warnings.append((2, "Moderate waves today — swim with caution and stay near lifeguards."))

    # --- Wind check (affects sea conditions) ---
    if wind_speed is not None:
        cards.append({"type": "wind", "value": wind_speed})
        if wind_speed > 25:
            warnings.append((2, "Strong winds are affecting sea conditions — check local advisories."))

    # --- Water temperature check ---
    if water_temperature is not None:
        cards.append({"type": "water_temperature", "value": water_temperature})
        if water_temperature < 20:
            warnings.append((1, "Water is on the cooler side today — a wetsuit is recommended."))

    # --- Tide (informational, not a warning) ---
    if tide is not None:
        cards.append({"type": "tide", "value": tide})

    if warnings:
        warnings.sort(key=lambda w: w[0], reverse=True)
        top_rank, top_message = warnings[0]
        priority_map = {3: "high", 2: "medium", 1: "low"}
        priority = priority_map[top_rank]
        message = top_message
        headline = "Check before you go in" if top_rank >= 2 else "Beach conditions today"
    else:
        priority = "low"
        message = "Sea conditions look good for a beach day."
        headline = "Great beach day"

    return _build_output(
        persona="beach",
        headline=headline,
        message_key="personalization.beach.auto_generated",
        message=message,
        priority=priority,
        cards=cards,
    )


def _handle_traveler(weather: dict) -> dict:
    """
    Sept 23: Real logic for the Traveler persona.

    Compares the user's current/home temperature against their
    destination's temperature, and gives packing suggestions based on
    the difference and destination rain conditions.
    """

    home_temp = weather.get("temperature")
    destination_temp = weather.get("destination_temperature")
    destination_condition = weather.get("destination_condition") or ""

    cards = []

    if home_temp is not None:
        cards.append({"type": "home_temperature", "value": home_temp})
    if destination_temp is not None:
        cards.append({"type": "destination_temperature", "value": destination_temp})

    # If we don't have both temperatures, we can't compare -- give a safe generic message.
    if home_temp is None or destination_temp is None:
        return _build_output(
            persona="traveler",
            headline="Travel weather",
            message_key="personalization.traveler.missing_data",
            message="Add your destination to see a packing suggestion.",
            priority="low",
            cards=cards,
        )

    diff = destination_temp - home_temp
    cards.append({"type": "temperature_difference", "value": diff})

    tips = []
    if diff >= 8:
        message = "Your destination is considerably warmer than here."
        tips.append("Pack light, breathable clothing.")
    elif diff <= -8:
        message = "Your destination is considerably cooler than here."
        tips.append("Pack a warm jacket or layers.")
    else:
        message = "Your destination's temperature is fairly similar to here."

    priority = "medium" if abs(diff) >= 8 else "low"

    # Rain check for the destination
    if "rain" in destination_condition.lower():
        tips.append("Carry a raincoat or umbrella — rain is expected at your destination.")
        priority = "medium"

    for tip in tips:
        cards.append({"type": "packing_tip", "value": tip})

    return _build_output(
        persona="traveler",
        headline="Before you pack",
        message_key="personalization.traveler.auto_generated",
        message=message,
        priority=priority,
        cards=cards,
    )


# ---------------------------------------------------------------------------
# SEPT 24: Universal occupation messages.
# Unlike the 4 core personas above (which each got their own function with
# custom rules), occupations share ONE generic function. Each occupation
# just needs 3 short messages (low/medium/high risk) in the dictionary
# below -- adding a new occupation later means adding a few lines here,
# not writing a whole new function.
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
    """A simple shared risk score reused by every occupation, based on
    rain probability and wind speed. This is intentionally simple — it's
    not meant to be as precise as the 4 core personas, just good enough
    to pick which of the 3 pre-written messages to show."""
    rain_probability = weather.get("rain_probability") or 0
    wind_speed = weather.get("wind_speed") or 0

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

    return _build_output(
        persona=persona,
        headline=headline,
        message_key=f"personalization.occupation.{persona}.{risk}",
        message=messages[risk],
        priority=risk,  # "low"/"medium"/"high" already match our priority values
        cards=cards,
    )


# ---------------------------------------------------------------------------
# SEPT 25: Foreigner climate comparison.
# Compares today's India temperature against the visitor's home country's
# typical climate, and gives simple packing tips.
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

    if profile is None or india_temp is None:
        return _build_output(
            persona="foreigner",
            headline="Visiting India?",
            message_key="personalization.foreigner.unknown_country",
            message="Select your home country to see a climate comparison.",
            priority="low",
            cards=[],
        )

    diff = india_temp - profile["avg_temperature"]
    tips = []

    if diff >= 8:
        climate_note = f"India today is considerably warmer than {profile['name']}."
        tips.append("Pack light, breathable clothing.")
        tips.append("Carry a water bottle and stay hydrated.")
    elif diff <= -8:
        climate_note = f"India today is considerably cooler than {profile['name']}."
        tips.append("Pack a light jacket or sweater.")
    else:
        climate_note = f"India today is fairly similar in temperature to {profile['name']}."

    rain_probability = weather.get("rain_probability") or 0
    if rain_probability >= 40:
        tips.append("Rain is likely — carry rain protection.")

    priority = "medium" if abs(diff) >= 8 else "low"

    cards = [{"type": "india_temperature", "value": india_temp}]
    for tip in tips:
        cards.append({"type": "tip", "value": tip})

    return _build_output(
        persona="foreigner",
        headline=f"Visiting from {profile['name']}?",
        message_key="personalization.foreigner.comparison",
        message=climate_note,
        priority=priority,
        cards=cards,
    )


# ---------------------------------------------------------------------------
# STEP 3: Shared helpers — every persona function uses these so the OUTPUT
# always matches the contract exactly, with no typos or missing fields.
# ---------------------------------------------------------------------------

def _build_output(persona: str, headline: str, message_key: str,
                   message: str, priority: str, cards: list) -> dict:
    """Guarantees every response has the exact shape the contract promises."""
    return {
        "persona": persona,
        "headline": headline,
        "message_key": message_key,
        "message": message,
        "priority": priority,
        "cards": cards,
    }


def _fallback_response(persona: str) -> dict:
    """Used when an unknown/unsupported persona is requested. Never crash."""
    return _build_output(
        persona=persona,
        headline="Welcome to MAUSAM",
        message_key="personalization.fallback.default",
        message="Personalized recommendations for this persona are coming soon.",
        priority="low",
        cards=[],
    )


# ---------------------------------------------------------------------------
# STEP 4: A quick manual test you can run directly with `python personalization_engine.py`
# This does NOT need FastAPI or the real weather backend — it's just to prove
# the skeleton works before anyone else depends on it.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_weather = {
        "temperature": 31,
        "humidity": 76,
        "wind_speed": 14,
        "uv_index": 8,
    }

    print("=== Basic pipeline test (all personas, Sept 19 style) ===")
    for test_persona in ["health", "fitness", "beach", "traveler", "unknown_persona"]:
        result = personalize(test_persona, sample_weather)
        print(f"\n--- Testing persona: {test_persona} ---")
        print(result)

    print("\n\n=== Sept 20: Health persona scenario tests ===")

    # Scenario 1: everything looks fine -> expect "All clear today", priority low
    mild_weather = {"aqi": 40, "uv_index": 3, "humidity": 55, "pollen_level": "low"}
    print("\n--- Health scenario: mild (should be 'All clear') ---")
    print(personalize("health", mild_weather))

    # Scenario 2: moderate concerns -> expect priority medium
    moderate_weather = {"aqi": 120, "uv_index": 7, "humidity": 65, "pollen_level": "moderate"}
    print("\n--- Health scenario: moderate (should be priority medium) ---")
    print(personalize("health", moderate_weather))

    # Scenario 3: severe conditions -> expect priority high, hazardous AQI message wins
    severe_weather = {"aqi": 250, "uv_index": 11, "humidity": 90, "pollen_level": "high"}
    print("\n--- Health scenario: severe (should be priority high, AQI message) ---")
    print(personalize("health", severe_weather))

    # Scenario 4: missing data -> must not crash, should fall back to safe default
    missing_weather = {}
    print("\n--- Health scenario: missing data (should not crash) ---")
    print(personalize("health", missing_weather))

    print("\n\n=== Sept 21: Fitness persona test ===")
    fitness_weather = {"temperature": 33, "wind_speed": 12, "rain_probability": 10, "sunrise": "06:02"}
    print(personalize("fitness", fitness_weather))

    print("\n\n=== Sept 22: Beach persona test ===")
    beach_weather = {"tide": "low", "wave_height_m": 1.8, "water_temperature": 26, "wind_speed": 15}
    print(personalize("beach", beach_weather))

    print("\n\n=== Sept 23: Traveler persona test ===")
    traveler_weather = {"temperature": 29, "destination_temperature": 12, "destination_condition": "Rainy"}
    print(personalize("traveler", traveler_weather))

    print("\n\n=== Sept 24: Universal occupation tests ===")
    occupation_weather_calm = {"rain_probability": 10, "wind_speed": 8}
    occupation_weather_risky = {"rain_probability": 70, "wind_speed": 35}
    for occupation in ["fisherman", "vendor", "delivery_worker", "gardener",
                        "student", "tourist", "sports_person", "it_professional", "homemaker"]:
        print(f"\n--- {occupation} (calm weather) ---")
        print(personalize(occupation, occupation_weather_calm))
        print(f"--- {occupation} (risky weather) ---")
        print(personalize(occupation, occupation_weather_risky))

    print("\n\n=== Sept 25: Foreigner comparison tests ===")
    india_weather = {"temperature": 33, "rain_probability": 50}
    for country_code in ["uk", "canada", "japan", "unknown_country"]:
        print(f"\n--- Visitor from: {country_code} ---")
        print(personalize("foreigner", india_weather, home_country=country_code))
