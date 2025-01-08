db = db.getSiblingDB('buzzdb');

db.games.drop();

db.games.insertMany([
    {
        name: "Mafia",
        description: "A social deduction game where innocent civilians try to identify the mafia among them while the mafia tries to remain hidden.",
        min_players: 6,
        max_players: 12,
        category: "social-deduction",
        duration_minutes: 30,
        thumbnail_url: "/static/images/games/mafia-thumbnail.webp",
        image_url: "/static/images/games/mafia.webp"
    },
    {
        name: "Spyfall",
        description: "Players try to discover who the spy is while the spy tries to figure out the location without revealing their identity.",
        min_players: 4,
        max_players: 8,
        category: "social-deduction",
        duration_minutes: 10,
        thumbnail_url: "/static/images/games/spyfall-thumbnail.webp",
        image_url: "/static/images/games/spyfall.webp"
    }
]);
