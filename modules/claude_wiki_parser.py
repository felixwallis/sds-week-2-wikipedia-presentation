import xml.etree.ElementTree as ET
import re
from pathlib import Path
import argparse


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

    def clean_wiki_markup(self, text):
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

    def extract_sections(self, text):
        """Extract sections from wiki text."""
        # Split text into sections based on headers
        sections = {}
        current_section = "Introduction"
        current_text = []

        for line in text.split('\n'):
            # Check for section headers
            header_match = re.match(r'==+\s*(.+?)\s*==+', line)

            if header_match:
                # Save previous section
                sections[current_section] = '\n'.join(current_text).strip()
                # Start new section
                current_section = header_match.group(1).strip()
                current_text = []
            else:
                current_text.append(line)

        # Add the last section
        sections[current_section] = '\n'.join(current_text).strip()

        return sections

    def extract_text_from_xml(self, xml_content):
        """Extract and clean text from Wikipedia XML."""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Find the text element
            text_elem = root.find('.//text')

            if text_elem is not None and text_elem.text:
                # Clean the wiki markup
                clean_text = self.clean_wiki_markup(text_elem.text)

                # Extract sections
                sections = self.extract_sections(clean_text)

                return sections

            return {"Error": "No text content found in XML"}

        except ET.ParseError:
            return {"Error": "Invalid XML format"}
        except Exception as e:
            return {"Error": f"An error occurred: {str(e)}"}


def process_file(input_file, output_file=None):
    """Process a Wikipedia XML file and save the cleaned text."""
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        # Extract and clean text
        extractor = WikiTextExtractor()
        sections = extractor.extract_text_from_xml(xml_content)

        # Prepare output
        output_text = []
        for section_name, section_text in sections.items():
            if section_text:  # Only include non-empty sections
                output_text.append(f"\n=== {section_name} ===\n")
                output_text.append(section_text)


        return output_text

        # # Determine output location
        # if output_file is None:
        #     input_path = Path(input_file)
        #     output_file = input_path.with_stem(
        #         input_path.stem + '_cleaned').with_suffix('.txt')

        # # Write output
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     f.write('\n'.join(output_text))

        # print(f"Successfully processed {input_file}")
        # print(f"Cleaned text saved to {output_file}")

    except Exception as e:
        print(f"Error processing file: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract and clean text from Wikipedia XML files')
    parser.add_argument('input_file', help='Path to the input XML file')
    parser.add_argument(
        '--output', '-o', help='Path to the output text file (optional)')

    args = parser.parse_args()
    process_file(args.input_file, args.output)


if __name__ == "__main__":
    main()

