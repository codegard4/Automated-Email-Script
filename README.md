# Automated-Email-Script

# Gas Price Scraper from Gas Buddy and Email Generation

This project is a Python script that fetches current gas prices from a list of GasBuddy station URLs, stores the data in a CSV file, filters the data by date, and sends the gas prices via email. The script retrieves prices for regular, midgrade, and premium fuel types. If the station offers other fuel types, those will be displayed as regular, midgrade and premium. Please verify with the original station URL the fuel types and make a note if any other fuel types are offered

## Features

- **Retrieve Gas Prices**: Retrieve gas prices from specified GasBuddy station URLs.
- **Store Data**: Save the retrieved gas prices to a CSV file.
- **Filter Data**: Filter gas prices for a specific date.
- **Format Data**: Format the gas prices as a text string for easy readability.
- **Send Email**: Send the formatted gas price data via email to specified recipients.

## Requirements

- Python 3.x
- `requests` library
- `beautifulsoup4` library
- `pandas` library
- `smtplib` module
- `email` module
- `datetime` module
- `os` module

You can install the necessary libraries using the following command:

```sh
pip install requests beautifulsoup4 pandas
