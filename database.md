# Database's Diagram (Mermaid)

```mermaid

erDiagram
    GUILD {
        INTEGER guild_id PK
    }

    CHANNELS {
        INTEGER channel_id PK
        INTEGER guild_id FK
    }

    SERIES {
        TEXT series_name PK
    }

    SERIES_ALIAS {
        TEXT alias_name PK
        TEXT series_name FK
    }

    USERS {
        INTEGER user_id PK
        TEXT username
    }

    LIKED {
        INTEGER user_id FK
        TEXT series_name FK
    }

    CARDS {
        INTEGER card_code PK
        INTEGER user_id FK
        INTEGER card_number
        INTEGER card_edition
        TEXT card_character
        TEXT card_series FK
    }

    CHANNELS }o--|| GUILD : "belongs to"
    SERIES_ALIAS }o--|| SERIES : "refers to"
    LIKED }o--|| USERS : "liked by"
    LIKED }o--|| SERIES : "likes"
    CARDS }o--|| USERS : "owned by"
    CARDS }o--|| SERIES : "from"
```

Channels table stores the channels where the bot is active, linked to their respective guilds. Each guild can have multiple channels.  
Series table contains the names of different series. Each series can have multiple aliases stored in the Series_Alias table.  
Users table holds information about users, including their unique IDs and usernames.  
Liked table tracks which users have liked which series. Each entry is linked to a user and a series.  
Cards table contains information about cards owned by users, including their attributes and the series they belong to.