# Anime Sama Scraper

This is a simple scraper for the Anime Sama website

# How to use

1. Clone the repository


2. Run the following command to install the dependencies

```bash
pip install -r requirements.txt
```

Then, don't forget to launch :

```bash
scrapling install
```

3. Run the script to start scraping the website with the following arguments :
- `--catalog` : scrape the catalog of anime/scan
- `--planning` : scrape the planning of anime/scan from the current week

```bash
python main.py --catalog
```

```bash
python main.py --planning
```

# Output

The output will be saved as a CSV file in the root directory of the project