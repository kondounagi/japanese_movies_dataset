# japanese_movies_dataset

## json schema
```
{
  "type": "object",
  "properties": {
    "isan": {
      "type": "string",
      "description": "International Standard Audiovisual Number"
    },
    "title": {
      "type": "string",
      "description": "The title of the movie"
    },  
    "sponsors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "corporate_name": {
            "type": "string"
          },
          "corporate_number": {
            "type": "integer"
          }
        }
      }
    },
    "distributors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "corporate_name": {
            "type": "string"
          },
          "corporate_number": {
            "type": "integer"
          }
        }
      }
    },
    "director": {
      "type": "string"
    },
    "scriptwriter": {
      "type": "string"
    },
    "performers": {
      "type": "string"
    },
    "production_studio": {
      "type": "string"
    },
    "screen_time": {
      "type": "integer"
      "description": "minute"
    },
    "release_data": {
      "type": "date"
    },
    "category": {
      "type": "string"
    },
    "sales": {
      "type": "integer",
      "description": "yen"
    },
    "production_cost": {
      "type": "integer",
      "description": "Japanese Yen"
    },
    "search_count": {
      "type": "integer"
    },
    "other_nominate": {
      "type": "array",
      "items": {
        "type": "object", 
        "properties": {
          "nominate_name": {
            "type": "string"
          }
        }
      }
    }
    "plot": {
      "type": "string"
    }
  }
}
```
