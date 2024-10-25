from pathlib import Path

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


if __name__ == '__main__':
    article_dir = Path.cwd() / 'data'
    
    # Check if directory exists
    if not article_dir.exists():
        print(f"Directory not found: {article_dir}")
    else:
        file_paths = fetch_file_paths(article_dir)
        print("Found files:")
        for path in file_paths:
            print(f"  {path}")