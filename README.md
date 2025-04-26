# CricInfo - Cricket Match Data Scraper

CricInfo is a Python-based web scraper designed to extract cricket match data from [Crex](https://crex.com/fixtures/match-list). The scraper collects information about upcoming, live, and completed matches, including match details, squads, live updates, and scorecards, and stores the data in structured JSON files.

## Features

- Scrapes cricket match details, squads, live updates, and scorecards.
- Stores data in JSON files for easy access and processing.
- Handles retries and error logging for robust scraping.
- Organized data storage for matches by match ID.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python (>= 3.8)
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/sarthaktayal174/CricInfo.git
   cd CricInfo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update `requirements.txt` if needed:
   - Ensure the following libraries are included:
     - `selenium`
     - `webdriver-manager`

4. Verify environment setup:
   - Ensure ChromeDriver is installed and accessible in your `PATH`.

## Usage

### Running the Scraper

1. Initialize the scraper:
   ```bash
   python -m scraper.match_scraper
   ```

2. Scraper Configuration:
   - Modify the `match_scraper.py` file to set the `match_url` and `match_id`.

3. Output:
   - Data will be stored in the `./data` directory in structured JSON files:
     - `info.json`: Match details
     - `squads.json`: Team squads
     - `live/latest.json`: Latest live updates
     - `scorecard/latest.json`: Latest scorecard data

4. Logs:
   - Check the `logs` directory for detailed logs of scraper activities.

### Debugging

If the scraper encounters issues:
- Check the logs for errors (e.g., data storage failures or website changes).
- Ensure the website structure hasn't changed.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your commit message"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue in the repository or contact [sarthaktayal174](https://github.com/sarthaktayal174).
