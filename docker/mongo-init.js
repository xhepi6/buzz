db = db.getSiblingDB('buzzdb');

db.games.drop();

db.games.insertMany([
    {
        name: "Mafia",
        slug: "mafia",
        description: "A social deduction game where innocent civilians try to identify the mafia among them while the mafia tries to remain hidden.",
        min_players: 3,
        max_players: 12,
        category: "social-deduction",
        duration_minutes: 30,
        thumbnail_url: "/static/images/games/mafia-thumbnail.webp",
        image_url: "/static/images/games/mafia.webp",
        settings: {
            roles: {
                min_mafia: 1,
                max_mafia: 4,
                optional_roles: ["doctor", "police", "moderator"]
            }
        }
    },
    {
        _id: "spyfall",
        name: "Spyfall",
        slug: "spyfall",
        description: "Players try to discover who the spy is while the spy tries to figure out the location without revealing their identity.",
        min_players: 4,
        max_players: 8,
        category: "social-deduction",
        duration_minutes: 10,
        thumbnail_url: "/static/images/games/spyfall-thumbnail.webp",
        image_url: "/static/images/games/spyfall.webp",
        locations: {
            "Airplane": "/static/images/spyfall_locations/airplane.webp",
            "Amusement Park": "/static/images/spyfall_locations/amusement_park.webp",
            "Aquarium": "/static/images/spyfall_locations/aquarium.webp",
            "Bank": "/static/images/spyfall_locations/bank.webp",
            "Beach": "/static/images/spyfall_locations/beach.webp",
            "Carnival": "/static/images/spyfall_locations/carnaval.webp",
            "Casino": "/static/images/spyfall_locations/casino.webp",
            "Castle": "/static/images/spyfall_locations/castle.webp",
            "Circus": "/static/images/spyfall_locations/circus.webp",
            "Construction Site": "/static/images/spyfall_locations/construction_site.webp",
            "Cyber Cafe": "/static/images/spyfall_locations/cybercaffe.webp",
            "Harbor": "/static/images/spyfall_locations/harbor.webp",
            "Haunted House": "/static/images/spyfall_locations/haunted_house.webp",
            "Hospital": "/static/images/spyfall_locations/hospital.webp",
            "Hotel": "/static/images/spyfall_locations/hotel.webp",
            "Jungle": "/static/images/spyfall_locations/jungle.webp",
            "Library": "/static/images/spyfall_locations/library.webp",
            "Mansion": "/static/images/spyfall_locations/mansion.webp",
            "Military Base": "/static/images/spyfall_locations/military_base.webp",
            "Movie Studio": "/static/images/spyfall_locations/movie_studio.webp",
            "Museum": "/static/images/spyfall_locations/museum.webp",
            "Oasis": "/static/images/spyfall_locations/oasis.webp",
            "Ocean Liner": "/static/images/spyfall_locations/ocean_liner.webp",
            "Opera House": "/static/images/spyfall_locations/opera.webp",
            "Pirate Ship": "/static/images/spyfall_locations/pirate_ship.webp",
            "Police Station": "/static/images/spyfall_locations/police_station.webp",
            "Power Plant": "/static/images/spyfall_locations/power_plant.webp",
            "Racing Track": "/static/images/spyfall_locations/racing_track.webp",
            "Restaurant": "/static/images/spyfall_locations/restaurant.webp",
            "School": "/static/images/spyfall_locations/school.webp",
            "Ski Resort": "/static/images/spyfall_locations/ski_resort.webp",
            "Space Station": "/static/images/spyfall_locations/space_station.webp",
            "Submarine": "/static/images/spyfall_locations/submarine.webp",
            "Supermarket": "/static/images/spyfall_locations/supermarket.webp",
            "Temple": "/static/images/spyfall_locations/temple.webp",
            "Theater": "/static/images/spyfall_locations/theater.webp",
            "Train": "/static/images/spyfall_locations/train.webp",
            "Underground Bunker": "/static/images/spyfall_locations/underground_bunker.webp",
            "University": "/static/images/spyfall_locations/university.webp",
            "Zoo": "/static/images/spyfall_locations/zoo.webp"
        },
        settings: {
            spy_count: {
                min: 1,
                max: 2
            },
            round_duration: {
                min: 5,
                max: 15
            }
        }
    }
]);
