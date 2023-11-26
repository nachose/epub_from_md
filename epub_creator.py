import os
import re
import sys
import pypandoc

def convert_markdown_to_epub(input_file, output_file):
    # Read the Markdown file
    with open(input_file, 'r') as f:
        markdown_content = f.read()

    # Find links and print them.
    find_links(markdown_content)

    # Extract links to other Markdown files
    links = extract_links(markdown_content)

    # Convert linked Markdown files recursively
    for link in links:
        linked_file = os.path.join(os.path.dirname(input_file), link)
        if os.path.isfile(linked_file):
            convert_markdown_to_epub(linked_file, output_file)

    # Convert the current Markdown file to EPUB
    pypandoc.convert_file(input_file, 'epub', outputfile=output_file)

def extract_links(markdown_content):
    # Regular expression to match Markdown links
    link_regex = r"\[(?P<link>.+?)\]\((?P<url>.+)\)"

    # Extract links from the Markdown content
    links = []
    for match in re.finditer(link_regex, markdown_content):
        # link = match.group('link')
        url = match.group('url')

        # Check if the link is a relative path to a Markdown file
        if url.startswith('./') or url.startswith('../'):
            links.append(url[2:])

    print (links)
    return links

def find_links(markdown_content):
    link_pattern = r'\[([^\]]+)\]\((http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)'
    links = re.findall(link_pattern, markdown_content)

    for link in links:
        print(f"Link text: {link[0]}")
        print(f"URL: {link[1]}")


if __name__ == '__main__':
    entrypoint_file = sys.argv[1]
    # entrypoint_file = 'documentation.md'  # Replace with the actual filename
    output_file = 'output.epub'

    convert_markdown_to_epub(entrypoint_file, output_file)

