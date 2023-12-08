import os
import re
import sys

# @brief convert_markdown_to_epub
#        Convert input file to just one epub.
#
# @param input_file      [in]    Input file. Beware the function is recursive
# @param recursion_depth [in]    recursion depth, for now just for debugging.
# @param added_links     [inout] links already added. This is because markdonw files,
#                                being unstructured, can have circular references, as is the case
#                                in which I'm working now.
# @param contents        [in]    Contents of the markdown file. I learnt today that string is immutable in python.
#
# @return Exit code.
def convert_markdown_to_epub(input_file,
                             recursion_depth,
                             added_links,
                             contents):

    contents = iterate_files(input_file, recursion_depth, added_links, contents)

    output_filename = get_output_filename(input_file)

    print_recursion(recursion_depth, input_file, output_filename)


    # Convert the current Markdown file to EPUB
    if recursion_depth == 1:
        write_files(contents, output_filename)

def iterate_files(input_file, recursion_depth, added_links, contents):
    # Read the Markdown file
    # print("Read markdown file: " + input_file)
    with open(input_file, 'r') as f:
        markdown_content = f.read()

    print("Adding to contents file " + input_file)
    contents = contents + markdown_content

    # Find links and print them.
    links = find_links(markdown_content)

    # Convert linked Markdown files recursively
    for link in links:
        # print (link)
        linked_file = os.path.join(os.path.dirname(input_file), str(link))
        # print ("linked_file " + linked_file)

        already_added = added_links.count(linked_file) > 0
        if already_added:
            print ("already added: " + linked_file)
            continue
        added_links.append(linked_file)
        if os.path.isfile(linked_file):
            # print("Call recursively to convert_markdown_to_epub")
            contents = iterate_files(linked_file,
                                     recursion_depth + 1,
                                     added_links,
                                     contents)
    return contents

def print_recursion(recursion_depth, input_file, output_filename):

    tabs_init = ''
    while(recursion_depth):
        tabs_init = tabs_init + "  "
        recursion_depth = recursion_depth -1
    # print(tabs_init + input_file + " to file " + output_filename)


def get_output_filename(input_file):

    output_filename = os.path.basename(input_file).removesuffix(".md") + ".epub"
    output_filename.replace(" ", "_")
    return output_filename

def write_files(content, output_file):

    #Replace images for it's true path.
    process_images(content)

    print("Write also markdown to file: result_markdown.md")
    g = open("result_markdown.md", "wt")
    g.write(content)
    g.close()


    print("Finally creating the file:")
    os.system("pandoc " + "result_markdown.md" + " -o " + output_file)

# Substitute routes for images. Taking into account that we are in the current directory, it must
# search for the images in the subdirectories, then use the correct path.
def process_images(content):
    find_images(content)


def find_links(markdown_content):
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, markdown_content)

    # for link in links:
    #     print(f"Link text: {link[0]}")
    #     print(f"URL: {link[1]}")

    files = []
    link_http = r'http'

    for link in links:
        #Do not add http links.
        if re.match(link_http, link[1]) :
            continue
        files.append(link[1])

    return files

def find_images(markdown_content):

    img_pattern = r'!\[.*\]\((.*\.jpg|.*\.jpeg|.*\.png)\)'
    images = re.findall(img_pattern, markdown_content)

    for img in images:
        print("Img found : " + img)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Usage python3 epub_creator.py entrypoint_file.md")
        exit (1)
    entrypoint_file = sys.argv[1]
    # entrypoint_file = 'documentation.md'  # Replace with the actual filename
    output_file = entrypoint_file.removesuffix('.md') + ".epub"

    added_links = []
    contents = ""

    convert_markdown_to_epub(entrypoint_file,
                             1,
                             added_links,
                             contents)

