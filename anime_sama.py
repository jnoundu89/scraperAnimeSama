import re

import pandas as pd

from logging_utils import LoggerManager
from request_utils import make_request_with_retries

o_logger = LoggerManager.get_logger(__name__)


async def anime_sama_catalog():
    base_url = "https://anime-sama.fr"
    catalog_url = f"{base_url}/catalogue/index.php"
    df = pd.DataFrame()
    o_logger.info(f"Getting data from {catalog_url}")
    fetcher = await make_request_with_retries(catalog_url)
    try:
        last_page = fetcher.find("div", {"id": "list_pagination"}).find_all("a").last.text
    except AttributeError:
        for _ in range(3):
            fetcher = await make_request_with_retries(catalog_url)
            try:
                last_page = fetcher.find("div", {"id": "list_pagination"}).find_all("a").last.text
                break
            except AttributeError:
                o_logger.warning(f"Could not get data from {catalog_url}")
                continue
    for page in range(1, int(last_page) + 1):
        url = f"{catalog_url}?page={page}"
        fetcher = await make_request_with_retries(url)
        data = fetcher.find("div", {"id": "list_catalog"}).find_all("div a")
        df_list = []
        for item in data:
            url = item.attrib["href"]
            image = item.find("img").attrib["src"]
            name = item.find("div h1").text
            elements = item.find("div").find_all("p")
            original_name = elements[0].text
            tag = elements[1].text
            category = elements[2].text
            language = elements[3].text
            df_list.append({
                'name': name,
                'original_name': original_name,
                'category': category,
                'tag': tag,
                'language': language,
                'url': url,
                'image': image
            })
            o_logger.info(f"Got data for {name}")
        o_logger.info(f"Page {page} done")
        df = pd.concat([df, pd.DataFrame(df_list)], ignore_index=True)
    df.to_csv("anime_sama_catalog.csv", index=False)


async def anime_sama_planning():
    base_url = "https://anime-sama.fr"
    base_image_path = "https://cdn.statically.io/gh/Anime-Sama/IMG/img/contenu/"
    planning_url = f"{base_url}/planning/"
    o_logger.info(f"Getting data from {planning_url}")
    fetcher = await make_request_with_retries(planning_url)

    def clean_script_content(content):
        patterns = [
            r'/\*.*?\*/',  # Remove /* ... */ comments
            r'//.*?\n',  # Remove // comments
            r'<script.*?>',  # Remove <script> tags
            r'</script>',  # Remove </script> tags
            r'document\.write\(.*?\);'  # Remove document.write(...)
        ]
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        return content

    def process_items(items, day="?", content_type=""):
        for element in items:
            item = [i.strip().replace("\"", "") for i in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', element)]
            df_list.append({
                'day': day,
                'name': item[0],
                'url': f"{base_url}/{item[1]}",
                'image': f"{base_image_path}{item[2]}.jpg",
                'release_hour': item[3],
                'status': item[4],
                "language": item[5],
                "type": content_type
            })

    df_list = []
    dict_day = {"Lundi": 1, "Mardi": 2, "Mercredi": 3, "Jeudi": 4, "Vendredi": 5, "Samedi": 6, "Dimanche": 0}

    all_data = [("?", fetcher.find("div", {"id": "sousBlocMiddle"}).find_all("h2").last.next.find("script").text)]

    for day_str, day_number in dict_day.items():
        data = fetcher.find("div", {"id": "planningClass"}).find_all("div", {"id": f"{day_number}"})
        for item in data:
            all_data.append((item.children.first.text.strip(), item.children.last.children.first.html_content))

    for day, content in all_data:
        cleaned_content = clean_script_content(content)
        for content_type, regex in [("anime", r'cartePlanningAnime\(([^)]+)\);'),
                                    ("scan", r'cartePlanningScan\(([^)]+)\);')]:
            process_items(re.findall(regex, cleaned_content), day, content_type)

    df = pd.DataFrame(df_list)
    df.to_csv("anime_sama_planning.csv", index=False)
    return df
