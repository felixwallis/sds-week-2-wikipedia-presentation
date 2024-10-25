import re
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup


class WikiTextExtractor:
    def __init__(self):
        self.template_pattern = r'\{\{[^\}]+\}\}'
        self.file_pattern = r'\[\[File:.*?\]\]'
        self.image_pattern = r'\[\[Image:.*?\]\]'
        self.ref_pattern = r'<ref.*?</ref>'
        self.ref_single_pattern = r'<ref.*?/>'
        self.html_pattern = r'<[^>]+>'
        self.wiki_link_pattern = r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]'
        self.multiple_newlines = r'\n+'
        self.multiple_spaces = r'\s+'
        self.table_pattern = r'\{\|.*?\|\}'
        self.category_pattern = r'\[\[Category:.*?\]\]'
        self.language_links = r'\[\[[a-z\-]+:[^\]]+\]\]'
        self.external_links = r'\[https?:[^\]]+\]'

    def clean_wiki_markup(self, text: str) -> str:
        """Remove wiki markup from text."""
        replacements = [
            (self.template_pattern, ''),        # Remove templates
            (self.file_pattern, ''),            # Remove file links
            (self.image_pattern, ''),           # Remove image links
            (self.ref_pattern, ''),             # Remove references
            (self.ref_single_pattern, ''),      # Remove single references
            (self.html_pattern, ''),            # Remove HTML tags
            (self.table_pattern, ''),           # Remove tables
            (self.category_pattern, ''),        # Remove category links
            (self.language_links, ''),          # Remove language links
            (self.external_links, ''),          # Remove external links
            # Keep link text, remove brackets
            (self.wiki_link_pattern, r'\1'),
            (self.multiple_newlines, '\n'),     # Normalize newlines
            (self.multiple_spaces, ' ')         # Normalize spaces
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text,
                          flags=re.MULTILINE | re.DOTALL)

        return text.strip()

    def extract_sections(self, text: str) -> list:
        """Extract sections from wiki text."""
        # Section header regex pattern
        section_pattern = r'==+\s*(.+?)\s*==+'

        # Find all headers and their positions
        header_matches = []
        matches = re.finditer(section_pattern, text, flags=re.MULTILINE)
        for match in matches:
            header_content = match.group(1).strip()
            start_pos = match.start()
            end_pos = match.end()
            header_matches.append((header_content, start_pos, end_pos))

        # Extract content between headers
        sections = []
        for i, (header, start_pos, end_pos) in enumerate(header_matches):
            # Check if this is the last header
            if i < len(header_matches) - 1:
                # Get the text between the current header and the next header
                next_start_pos = header_matches[i + 1][1]
                section_text = text[end_pos:next_start_pos].strip()
            else:
                section_text = text[end_pos:].strip()
            sections.append((header, section_text))

        return sections

    def extract_text_from_xml(self, xml_content) -> list:
        """Extract and clean text from XML."""
        try:
            # Parse XML with BeautifulSoup
            soup = BeautifulSoup(xml_content, 'lxml')

            # Find the text element (using find() as there is only one text element per article)
            text_elem = soup.find('text')
            if text_elem and text_elem.string:
                # Clean the wiki markup
                clean_text = self.clean_wiki_markup(text_elem.string)
                # Extract sections
                sections = self.extract_sections(clean_text)

                return sections

            raise Exception('No text content found in XML.')

        except Exception as e:
            return {'Error': f'An error occurred: {str(e)}'}

    def extract_metadata_from_xml(self, xml_content) -> dict:
        """Extract the XML's metadata."""
        try:
            soup = BeautifulSoup(xml_content, 'lxml')
            metadata = {
                'id': soup.find('id').string if soup.find('id') else None,
                'timestamp': soup.find('timestamp').string if soup.find('timestamp') else None,
                'contributor': soup.find('username').string if soup.find('username') else None,
            }

            return metadata
        
        except Exception as e:
            return {'Error': f'An error occurred: {str(e)}'}


def process_file(input_file) -> pd.DataFrame:
    """Process a Wikipedia XML file and save the cleaned text."""
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

            # Extract and clean text
            extractor = WikiTextExtractor()
            metadata = extractor.extract_metadata_from_xml(xml_content)
            sections = [
                {'section_name': name, 'section_text': text}
                for name, text in extractor.extract_text_from_xml(xml_content)
                if text  # Filter out empty sections]
            ]

        # Broadcase metadata to all sections
        file_df = pd.DataFrame(sections).assign(**metadata)
        file_df.set_index('timestamp', inplace=True)
        
        return file_df

    except Exception as e:
        print(f'Error processing {input_file}: {str(e)}')


if __name__ == "__main__":
    df = process_file('/Users/felixwallis/Desktop/Oxford MSc/Oxford Social Data Science Course/Fundamentals for Social Data Science in Python/sds-week-2-wikipedia-presentation/data/Vladimir_Putin/2022/11/1121654865.xml')
    df.to_csv('/Users/felixwallis/Desktop/Oxford MSc/Oxford Social Data Science Course/Fundamentals for Social Data Science in Python/sds-week-2-wikipedia-presentation/data/1121654865.csv')
