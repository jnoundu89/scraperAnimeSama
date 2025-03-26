import argparse
import asyncio
import os

from anime_sama import anime_sama_catalog, anime_sama_planning
from logging_utils import LoggerManager

s_script_name = os.path.basename(os.path.dirname(__file__))
LoggerManager(log_level='INFO', process_name=s_script_name)

o_logger = LoggerManager.get_logger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Scrape data from Anime Sama website")
    parser.add_argument('--catalog', action='store_true', help="Scrape Anime Sama catalog")
    parser.add_argument('--planning', action='store_true', help="Scrape Anime Sama planning of the week")
    args = parser.parse_args()

    if args.catalog:
        await anime_sama_catalog()
    elif args.planning:
        await anime_sama_planning()
    else:
        print("Please provide either --catalog or --planning argument")


if __name__ == '__main__':
    asyncio.run(main())
