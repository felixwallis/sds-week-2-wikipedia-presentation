import pandas as pd
from pathlib import Path
from tqdm import tqdm
from wiki_parser import process_file

def fetch_file_paths(article_dir: Path) -> list:
    """Fetch file paths recursively from a directory."""
    file_paths = []
    try:
        for item_path in article_dir.iterdir():
            if item_path.is_dir():
                # Recursively get files from subdirectories and extend the list
                file_paths.extend(fetch_file_paths(item_path))
            else:
                file_paths.append(item_path)
                
    except Exception as e:
        print(f"Error accessing {article_dir}: {e}")

    return file_paths


def file_paths_to_df(file_paths: list):
    """Convert a list of file paths to a DataFrame."""    
    file_data = [process_file(file) for file in tqdm(file_paths)]
    df = pd.concat(file_data)

    return df


if __name__ == '__main__':
    article_dir = Path.cwd() / 'data'
    
    file_paths = fetch_file_paths(article_dir)
    file_data = file_paths_to_df(file_paths)  

    # print(file_data)