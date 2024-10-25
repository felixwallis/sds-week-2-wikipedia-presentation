import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup


def extract_text_from_article(xml_file: Path) -> pd.DataFrame:
    """Extract the text from an XML file and return it in a DataFrame."""
    article_name = xml_file.stem

    xml_content = xml_file.read_text()
    soup = BeautifulSoup(xml_content, "xml")

    text_elem = soup.find_all("text")

    return pd.DataFrame({"article_name": article_name, "text": text_elem})


if __name__ == "__main__":
    xml_file = Path().cwd() / "data" / "Xi_Jinping" / \
        "2023" / "01" / "1130931521.xml"
