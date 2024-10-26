#Importing required libraries/dependencies
import re
from bs4 import BeautifulSoup
import os
from pathlib import Path
import pandas as pd
from collections import defaultdict

class WikiXMLParser:
    def __init__(self):
        # Define regex patterns for various types of wiki markup
        self.template_pattern = r'\{\{[^\}]+\}\}'  # Templates
        self.file_pattern = r'\[\[File:.*?\]\]'    # File links
        self.image_pattern = r'\[\[Image:.*?\]\]'   # Image links
        self.ref_pattern = r'<ref.*?</ref>'        # References
        self.ref_single_pattern = r'<ref.*?/>'
        self.html_tag_pattern = r'<[^>]+>'          # HTML tags
        self.wiki_link_pattern = r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]'  # Wiki links
        self.multiple_newlines_pattern = r'\n+'     # Multiple newlines
        self.multiple_spaces_pattern = r'\s+'       # Multiple spaces
        self.table_pattern = r'\{\|.*?\|\}'         # Tables
        self.category_pattern = r'\[\[Category:.*?\]\]'  # Category links
        self.language_links_pattern = r'\[\[[a-z\-]+:[^\]]+\]\]'  # Language links
        self.external_links_pattern = r'\[https?:[^\]]+\]'  # External links
        self.numeric_stopwords_pattern = r'\b\d+\b'         # Numerical stopwords
        
        # Patterns for removing unwanted abrupt content
        self.timestamp_pattern = r'\d{2}T\d{2}:\d{2}:\d{2}Z'  # Timestamps in format YYYY-MM-DDTHH:MM:SSZ
        self.header_pattern = r'={2,}.*?={2,}'                # Section headers (e.g., === Header ===)
        self.random_chars_pattern = r'\s*[-*]+\s*'            # Random characters like -- or * *
        self.abrupt_content_pattern = r'\|\s*.*?[^a-zA-Z0-9]'  # Abrupt random strings

    def clean_wiki_markup(self, raw_text):
        """
        Clean the raw Wikipedia markup by removing unnecessary elements and formatting the text.
        
        Args:
            raw_text (str): The raw text extracted from the Wikipedia XML.
            
        Returns:
            str: The cleaned and formatted text.
        """
        # Replace common HTML entities
        cleaned_text = raw_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

        # List of tuples containing regex patterns and their replacements
        replacements = [
            (self.template_pattern, ''),              # Remove templates
            (self.file_pattern, ''),                  # Remove file links
            (self.image_pattern, ''),                 # Remove image links
            (self.ref_pattern, ''),                   # Remove references
            (self.ref_single_pattern, ''),            # Remove single references
            (self.html_tag_pattern, ''),              # Remove HTML tags
            (self.table_pattern, ''),                 # Remove tables
            (self.category_pattern, ''),              # Remove category links
            (self.language_links_pattern, ''),        # Remove language links
            (self.external_links_pattern, ''),        # Remove external links
            (self.wiki_link_pattern, r'\1'),          # Keep link text, remove brackets
            (self.multiple_newlines_pattern, '\n'),   # Normalize newlines
            (self.multiple_spaces_pattern, ' '),      # Normalize spaces
            (self.numeric_stopwords_pattern, ''),     # Remove numeric stopwords
            (self.timestamp_pattern, ''),              # Remove timestamps
            (self.header_pattern, ''),                 # Remove section headers
            (self.random_chars_pattern, ''),           # Remove random characters
            (self.abrupt_content_pattern, '')          # Remove abrupt content
        ]

        # Apply all replacements using regex
        for pattern, replacement in replacements:
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.MULTILINE | re.DOTALL)

        return cleaned_text.strip()  # Return cleaned text without leading/trailing spaces

    def extract_sections_from_wiki_xml(self, xml_file_path):
        """
        Extract section titles and their corresponding text content from a Wikipedia XML dump file.
        
        Args:
            xml_file_path (str): Path to the Wikipedia XML dump file
            
        Returns:
            list: A list of dictionaries containing section titles and their content
        """
        sections = []  # Initialize list to store section data
        section_title_pattern = r'^={2,}([^=]+)={2,}'  # Regex for section headings
        inside_revision_content = False  # Flag to indicate if we're within <rev> tags
        revision_content = []  # Store lines of text within <rev> tags

        # Read the XML content from the specified file
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()  # Read the entire file content
            
            # Process each line in the XML content
            for line in xml_content.splitlines():
                # Check if we are entering revision content
                if '<rev' in line:
                    inside_revision_content = True
                    continue

                # Check if we are exiting revision content
                if '</rev>' in line:
                    inside_revision_content = False
                    continue

                # Process lines only when we are within revision content
                if inside_revision_content:
                    # Look for section headings in the line
                    section_title_match = re.match(section_title_pattern, line.strip())
                    if section_title_match:
                        section_title = section_title_match.group(1).strip()  # Extract the section title
                        heading_level = line.count('=') // 2  # Calculate heading level

                        # If it's a level 2 heading, create a new section
                        if heading_level == 2:
                            # Join and clean the content for the current section
                            section_text = '\n'.join(revision_content).strip()
                            sections.append({
                                'title': section_title,
                                'text': self.clean_wiki_markup(section_text)  # Clean the section text
                            })

                            # Clear revision_content for the next section
                            revision_content = []
                        else:
                            # If it's a subheading (level 3 or 4), just append to revision_content
                            revision_content.append(f'=== {section_title} ===')  # Mark subheadings

                    else:
                        # If no heading is found, continue appending content
                        revision_content.append(line.strip())

            # Handle the last section after exiting <rev>
            if revision_content:
                section_text = '\n'.join(revision_content).strip()
                last_section_title = 'Last Section'
                sections.append({
                    'title': last_section_title,
                    'text': self.clean_wiki_markup(section_text)  # Clean the last section text
                })

        return sections

    def extract_sections_to_dataframe(self, xml_file_path):
        """
        Extract sections from a Wikipedia XML file and return as a DataFrame.
        
        Args:
            xml_file_path (str): Path to the Wikipedia XML dump file
            
        Returns:
            pd.DataFrame: DataFrame containing section titles and their content
        """
        extracted_sections = self.extract_sections_from_wiki_xml(xml_file_path)

        df = pd.DataFrame(extracted_sections)

        # Normalize the path to handle different separators
        normalized_path = os.path.normpath(xml_file_path)

        # Split the path into components
        components = normalized_path.split(os.sep)

        # Extract the last components
        df['file_id'] = components[-1].replace('.xml', '')  # Remove the .xml extension
        df["month"] = components[-2]  # Month
        df["year"] = components[-3]   # Year
        df["article_name"] = components[-4]  # Article name

        return df  # Convert list of sections to DataFrame
    



"""
The class below will be used for handling and understanding the different titles/sections present along the history of revisoins for the wiki articles
"""

class WikiSectionAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.section_tracker = defaultdict(lambda: defaultdict(set))
        self.timeline = []

    def get_last_revision_file(self, month_dir):
        """
        Get the file with the highest revision number in a given directory.
        """
        files = [f for f in os.listdir(month_dir) if f.endswith('.xml')]
        if not files:
            return None
        
        # Sort by revision number (assuming filename format includes revision at the end)
        files.sort(key=lambda x: int(re.findall(r'\d+', x)[-1]))
        return files[-1]

    def extract_sections_from_wiki_xml(self, file_path):
        """
        Extract section titles from Wikipedia XML dump file using direct file reading and regex.
        Handles Wikipedia dump XML structure where content is within <rev> tags.
        """
        sections = []
        section_pattern = r'^={2,}([^=]+)={2,}'
        in_rev_content = False

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Check if we're entering revision content
                if '<rev' in line:
                    in_rev_content = True
                    continue
                    
                # Check if we're exiting revision content
                if '</rev>' in line:
                    in_rev_content = False
                    continue
                
                # Only process lines when we're inside revision content
                if in_rev_content:
                    # Look for section headings
                    match = re.match(section_pattern, line.strip())
                    if match:
                        section_title = match.group(1).strip()
                        level = line.count('=') // 2  # Calculate heading level
                        
                        sections.append({
                            'title': section_title,
                            'level': level
                        })

        return sections

    def analyze_section_evolution(self):
        """
        Analyze section titles across all XML files in the directory structure.
        """
        # Walk through the year/month directory structure
        for year_dir in sorted(os.listdir(self.base_dir)):
            year_path = Path(self.base_dir) / year_dir
            if not year_path.is_dir() or not year_dir.isdigit():
                continue
                
            for month_dir in sorted(os.listdir(year_path)):
                month_path = year_path / month_dir
                if not month_path.is_dir() or not month_dir.isdigit():
                    continue
                    
                # Get the last revision file for this month
                last_revision = self.get_last_revision_file(month_path)
                if not last_revision:
                    continue
                    
                xml_file = month_path / last_revision
                date_str = f"{year_dir}-{month_dir}"
                
                # Extract sections from the XML file
                sections = self.extract_sections_from_wiki_xml(xml_file)
                
                # Track sections for this date
                for section in sections:
                    self.section_tracker[section['title']][date_str].add(section['level'])
                    
                self.timeline.append(date_str)

        return self.section_tracker, sorted(self.timeline)

    def create_section_evolution_report(self):
        """
        Create a DataFrame showing section title evolution over time.
        """
        # Create a DataFrame with dates as columns and sections as rows
        data = []
        for section, date_levels in self.section_tracker.items():
            row = {'Section': section}
            for date in sorted(self.timeline):
                levels = date_levels.get(date, set())
                row[date] = ','.join(str(l) for l in sorted(levels)) if levels else ''
            data.append(row)
        
        df = pd.DataFrame(data)
        df = df.set_index('Section')
        return df

    def get_sections_by_year_dict(self, evolution_df, heading_level):
        """
        Extract second-level headings for each year from the evolution DataFrame.
        """
        # Initialize dictionary to store yearly sections
        yearly_sections = {}
        
        # Get all unique years from column names
        years = sorted(set(col.split('-')[0] for col in evolution_df.columns))
        
        for year in years:
            # Get columns for this year
            year_columns = [col for col in evolution_df.columns if col.startswith(year)]
            
            # Get sections that appear as level 2 in any month of this year
            year_sections = []
            for section in evolution_df.index:
                # Get all values for this section across the year's months
                section_levels = evolution_df.loc[section, year_columns]
                
                # Check if "2" appears in any month
                is_level_2 = section_levels.apply(
                    lambda x: isinstance(x, str) and heading_level in x.split(',')
                ).any()
                
                if is_level_2:
                    year_sections.append(section)
            
            yearly_sections[year] = sorted(year_sections)
        
        return yearly_sections

    def main_parse(self):
        """
        Main function to process Wikipedia XML files and generate reports.
        """
        # Analyze section evolution
        print("Analyzing section evolution...")
        self.analyze_section_evolution()

        # Create and save the evolution report
        print("Creating section evolution report...")
        evolution_df = self.create_section_evolution_report()

        return evolution_df



# Extra Functions

def get_xml_file_paths(directory):
    """
    Retrieve a list of XML file paths within a specified directory structure.

    This function traverses the given directory and its subdirectories to find
    all XML files located exactly two levels deeper than the specified directory.
    
    Parameters:
    directory (str): The path to the directory where the search begins.
                     It should contain subdirectories, where the function 
                     looks for XML files in subdirectories that are two levels deep.

    Returns:
    list: A list of strings representing the full paths of XML files found 
          in the specified directory structure. If no XML files are found, 
          an empty list is returned.

    Example:
    >>> xml_files = get_xml_file_paths('/path/to/your/directory')
    >>> for xml_file in xml_files:
    ...     print(xml_file)
    """
    xml_file_paths = []
    
    # Traverse the directory structure
    for root, dirs, files in os.walk(directory):
        # Check if the current directory is two levels deeper
        if root.count(os.sep) - directory.count(os.sep) == 2:
            for file in files:
                # Check if the file has a .xml extension
                if file.endswith('.xml'):
                    # Append the full path of the XML file to the list
                    xml_file_paths.append(os.path.join(root, file))
    
    return xml_file_paths