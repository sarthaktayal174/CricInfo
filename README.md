# CricInfo - Cricket Match Data Scraper

CricInfo is a Python-based web scraper designed to extract cricket match data from [Crex](https://crex.com/fixtures/match-list). The scraper collects information about upcoming, live, and completed matches, including match details, squads, live updates, and scorecards, and stores the data in structured JSON files.

## Features

- Live match tracking
- Scorecard scraping
- Team squads information
- Match list updates
- REST API endpoints
- Automated scheduling
- MongoDB data storage
- Docker containerization

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python (>= 3.8)
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- Docker
- Docker Compose
- Git

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/sarthaktayal174/CricInfo.git
   cd CricInfo
   ```

2. Build and start the containers:
```bash
docker-compose up --build
```

3. To run in detached mode:
```bash
docker-compose up -d
```

4. To stop the application:
```bash
docker-compose down
```

## Project Structure

```
CricInfo/
├── scraper/
│   ├── match_scraper.py    # Match data scraping logic
│   ├── data_store.py       # MongoDB data storage
│   ├── scheduler.py        # Background task scheduling
│   └── types.py           # Type definitions
├── main.py                # Main application entry
├── api.py                 # REST API endpoints
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── CHANGELOG.md          # Version history
```

## Configuration

### Environment Variables

- `MONGODB_URI`: MongoDB connection string (default: mongodb://mongodb:27017/)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)
- `DISPLAY`: X11 display for Chrome (default: :99)

### Volumes

- `./logs`: Application logs
- `mongodb_data`: MongoDB data persistence

## API Endpoints

- `GET /matches`: List all matches
- `GET /matches/<match_id>`: Get specific match details
- `GET /matches/live`: Get live matches
- `GET /matches/upcoming`: Get upcoming matches
- `GET /matches/completed`: Get completed matches

## Data Storage

The application uses MongoDB to store:
- Match lists
- Live match data
- Scorecards
- Team squads
- Match information

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application locally:
```bash
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Video explanation link
`https://drive.google.com/file/d/1kjquyYYeLJAOe3qSP0UOScl_jJmnbAFb/view?usp=sharing`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue in the repository or contact [sarthaktayal174](https://github.com/sarthaktayal174).
