from app.services.firebase_service import db


def save_location(city: str, latitude: float, longitude: float):
    location_ref = db.collection("saved_locations").document()

    location_data = {
        "city": city,
        "latitude": latitude,
        "longitude": longitude
    }

    location_ref.set(location_data)

    return {
        "id": location_ref.id,
        **location_data
    }
def get_saved_locations():
    locations = []

    docs = db.collection("saved_locations").stream()

    for doc in docs:
        location = doc.to_dict()

        locations.append({
            "id": doc.id,
            **location
        })

    return locations