import argparse
from collections.abc import Callable, Generator
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

DATA_DIR = Path("data")


def download_page_w_revisions(page_title: str, since: datetime) -> Generator[str, None, None]:
    """
    Fetch all revisions of a Wikipedia page since the specified date using the MediaWiki API.
    Yields each revision as an XML string.
    """
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "xml",
        "prop": "revisions",
        "titles": page_title,
        "rvprop": "ids|timestamp|user|comment|content",
        "rvlimit": "max",  # Maximum allowed per request (500 for regular users)
        "rvdir": "newer",  # Fetch revisions in ascending order
        # "formatversion": "2",  # REMOVE THIS LINE
        "rvstart": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    while True:
        response = S.get(url=URL, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml-xml")

        # Check if the page exists
        page = soup.find("page")
        if page is None or page.get("missing") is not None:
            raise ValueError(f"Page '{page_title}' does not exist.")

        revisions = soup.find_all("rev")
        if not revisions:
            break  # No more revisions to process

        for rev in revisions:
            # Convert the <rev> tag back to XML string
            revision_xml = str(rev)
            yield revision_xml

        # Check if there is a continuation
        cont = soup.find("continue")
        if cont and cont.get("rvcontinue"):
            params["rvcontinue"] = cont.get("rvcontinue")
        else:
            break  # No more pages


def parse_mediawiki_revisions(xml_content: str) -> Generator[str, None, None]:
    """
    Parses the XML content and yields each revision as a string.
    """
    soup = BeautifulSoup(xml_content, "lxml-xml")
    for revision in soup.find_all("rev"):
        yield str(revision)


def _extract_attribute(text: str, attribute: str) -> str:
    soup = BeautifulSoup(text, "lxml-xml")
    rev_tag = soup.find('rev')
    if rev_tag is None:
        raise ValueError("No 'rev' tag found in text")
    result = rev_tag.get(attribute)
    if result is None:
        raise ValueError(f"Could not find attribute '{attribute}' in 'rev' tag")
    return result


def find_timestamp(revision: str) -> datetime:
    timestamp_str = _extract_attribute(revision, attribute="timestamp")
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")


def extract_id(revision: str) -> str:
    return _extract_attribute(revision, attribute="revid")


def _extract_yearmonth(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m")


def find_yearmonth(revision: str) -> str:
    return _extract_yearmonth(find_timestamp(revision))


def construct_path(page_name: str, save_dir: Path, wiki_revision: str) -> Path:
    revision_id = extract_id(wiki_revision)
    timestamp = find_timestamp(wiki_revision)
    year = str(timestamp.year)
    month = str(timestamp.month).zfill(2)
    revision_path = save_dir / page_name / year / month / f"{revision_id}.xml"
    return revision_path


def count_revisions(revisions_dir: Path) -> int:
    return sum(1 for _ in revisions_dir.rglob("*.xml"))


def _extract_yearmonth_from_path(path: Path) -> str:
    return f"{path.parent.parent.name}-{path.parent.name}"


def _find_yearmonth_with_func(revisions_dir: Path, sort_func: Callable) -> str:
    try:
        sorted_file = sort_func(revisions_dir.rglob("*.xml"), key=lambda p: p.stat().st_mtime)
        return _extract_yearmonth_from_path(sorted_file)
    except ValueError:
        return "N/A"


def find_first_revision_yearmonth(revisions_dir: Path) -> str:
    return _find_yearmonth_with_func(revisions_dir, min)


def find_last_revision_yearmonth(revisions_dir: Path) -> str:
    return _find_yearmonth_with_func(revisions_dir, max)


def download_revisions(page: str, data_dir: Path, since: datetime, update: bool = False) -> None:
    page_directory = data_dir / page
    if not update and page_directory.exists():
        print(f"Page '{page}' already exists. Skipping download.")
        return

    print(f"Downloading revisions for '{page}' since {since.strftime('%Y-%m-%d')}...")
    try:
        revisions_generator = download_page_w_revisions(page, since)
        saved_revisions = 0
        for wiki_revision in tqdm(revisions_generator, desc="Downloading Revisions"):
            revision_timestamp = find_timestamp(wiki_revision)
            if revision_timestamp >= since:
                revision_path = construct_path(
                    page_name=page, save_dir=data_dir, wiki_revision=wiki_revision
                )
                if not revision_path.exists():
                    revision_path.parent.mkdir(parents=True, exist_ok=True)
                    revision_path.write_text(wiki_revision)
                    saved_revisions += 1
        print(f"Done! Saved {saved_revisions} revisions after {since.strftime('%Y-%m-%d')}.")
    except Exception as e:
        print(f"An error occurred while downloading revisions: {e}")


def validate_page(page_name: str, page_xml: str) -> None:
    try:
        _ = _extract_attribute(page_xml, attribute="page")
    except ValueError:
        raise ValueError(f"Page '{page_name}' does not exist")


def main(page: str, data_dir: Path, since: datetime, update: bool = False):
    """
    Downloads the main page (with revisions) for the given page title.
    Organizes the revisions into a folder structure like
    <page_name>/<year>/<month>/<revision_id>.xml
    """
    download_revisions(page, data_dir, since, update)

    revision_count = count_revisions(data_dir / page)
    if revision_count > 0:
        max_yearmonth = find_last_revision_yearmonth(data_dir / page)
        min_yearmonth = find_first_revision_yearmonth(data_dir / page)
        print(
            f"Page '{page}' has {revision_count} revisions between {min_yearmonth} and {max_yearmonth}"
        )
    else:
        print(f"No revisions found for page '{page}' after {since.strftime('%Y-%m-%d')}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download Wikipedia page revisions after a specified date",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("page", type=str, help="Title of the Wikipedia page")
    parser.add_argument(
        "--since",
        type=str,
        required=True,
        help="Download revisions after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--update", action="store_true", help="Should new data be updated?"
    )
    args = parser.parse_args()

    try:
        since_date = datetime.strptime(args.since, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect date format for --since. Expected YYYY-MM-DD.")

    main(page=args.page, data_dir=DATA_DIR, since=since_date, update=args.update)
