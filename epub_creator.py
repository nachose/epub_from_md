import os
import pandoc

def convert_markdown_to_epub(input_file, output_file):
    # Read the Markdown file
    with open(input_file, 'r') as f:
        markdown_content = f.read()

    # Extract links to other Markdown files
    links = extract_links(markdown_content)

    # Convert linked Markdown files recursively
    for link in links:
        linked_file = os.path.join(os.path.dirname(input_file), link)
        if os.path.isfile(linked_file):
            convert_markdown_to_epub(linked_file, output_file)

    # Convert the current Markdown file to EPUB
    pandoc.convert_file(input_file, 'epub', output=output_file)

def extract_links(markdown_content):
    # Regular expression to match Markdown links
    link_regex = r"\[(?P<link>.+?)\]\((?P<url>.+)\)"

    # Extract links from the Markdown content
    links = []
    for match in re.finditer(link_regex, markdown_content):
        link = match.group('link')
        url = match.group('url')

        # Check if the link is a relative path to a Markdown file
        if url.startswith('./') or url.startswith('../'):
            links.append(url[2:])

    return links

if __name__ == '__main__':
    entrypoint_file = 'documentation.md'  # Replace with the actual filename
    output_file = 'documentation.epub'

    convert_markdown_to_epub(entrypoint_file, output_file)

