# MAUSAM — Personalization Engine Contract
### Owner: Person 4 (Personalization Engine)  |  Date: Sept 18

This is the agreed shape of data going IN and OUT of the personalization engine.
Person 1 (tech lead) wires this into `/api/home`.
Person 3 (weather backend) must supply weather data matching the field names below.
Person 2 (UI) builds `RecommendationCard` to render the OUTPUT shape below, for any persona.

---

## INPUT (what the engine receives)

```json
{
  "persona": "fitness",
  "weather": {
    "temperature": 31,
    "humidity": 76,
    "wind_speed": 14,
    "rain_probability": 20,
    "condition": "Partly Cloudy",
    "uv_index": 8,
    "aqi": 90,
    "pollen_level": "moderate",
    "sunrise": "06:02",
    "sunset": "18:15",
    "tide": "low",
    "wave_height_m": 1.2,
    "water_temperature": 27,
    "destination_temperature": 18,
    "destination_condition": "Rainy"
  },
  "language": "en"
}
```

**Notes:**
- `persona` will be one of: `"health"`, `"fitness"`, `"beach"`, `"traveler"`, or a universal-occupation string like `"fisherman"`, `"vendor"`, `"gardener"`, etc. (added Sept 24).
- Not every weather field is relevant to every persona — the `health` engine ignores `tide`, for example. Fields the current weather source doesn't provide yet may be `null` — code must handle that, never assume every field exists.
- `destination_*` fields only apply to `"traveler"` persona (weather at the place they're traveling to).

---

## OUTPUT (what the engine returns)

```json
{
  "persona": "fitness",
  "headline": "Good morning, runner!",
  "message_key": "personalization.fitness.best_hours",
  "message": "Better outdoor activity window before 8 AM.",
  "priority": "medium",
  "cards": [
    { "type": "best_running_hours", "value": "6:00 AM – 8:00 AM" },
    { "type": "wind", "value": "14 km/h" },
    { "type": "uv", "value": 8 }
  ]
}
```

**Notes:**
- `priority` is always one of: `"low"`, `"medium"`, `"high"` — this lets the UI decide how loudly to show the card.
- `message_key` is a placeholder for Person 6 (localization) — by Sept 26 every hardcoded `message` string gets replaced by a lookup through this key. Include it from Day 1 even before translations exist.
- `cards` is a list — can be empty `[]`, can have 1 or many. The UI loops over this list and renders one small tile per entry, regardless of persona.

---

## Handoff checklist for Sept 18
- [ ] Share this file with Person 1 — this becomes part of `/api/home`'s response.
- [ ] Confirm with Person 3 that these exact weather field names (`temperature`, `uv_index`, etc.) are what the `/weather` endpoint will actually return — rename here now if theirs differ, before any code is written.
