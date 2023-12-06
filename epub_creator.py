import os
import re
import sys

# @brief convert_markdown_to_epub 
#        Convert input file to just one epub. 
#
# @param input_file      [in]    Input file. Beware the function is recursive
# @param output_file     [in]    Output file, as the end goal is to have just
#                                one output file.
# @param recursion_depth [in]    recursion depth, for now just for debugging.
# @param added_links     [inout] links already added. This is because markdonw files,
#                                being unstructured, can have circular references, as is the case
#                                in which I'm working now.
#
# @return Exit code.
def convert_markdown_to_epub(input_file, output_file, recursion_depth, added_links):
    # Read the Markdown file
    # print("Read markdown file: " + input_file)
    with open(input_file, 'r') as f:
        markdown_content = f.read()

    # Find links and print them.
    links = find_links(markdown_content)

    # Convert linked Markdown files recursively
    for link in links:
        # print (link)
        linked_file = os.path.join(os.path.dirname(input_file), str(link))
        print ("linked_file " + linked_file)

        already_added = added_links.count(linked_file) > 0
        if already_added:
            print ("already added: " + linked_file)
            continue
        added_links.append(linked_file)
        if os.path.isfile(linked_file):
            # print("Call recursively to convert_markdown_to_epub")
            convert_markdown_to_epub(linked_file,
                                     output_file,
                                     recursion_depth + 1,
                                     added_links)

    output_filename = os.path.basename(input_file) + ".epub"
    output_filename.replace(" ", "_")

    # Convert the current Markdown file to EPUB
    # os.system("pandoc " + input_file + " -o " + output_filename)
    tabs_init = ''
    while(recursion_depth):
        tabs_init = tabs_init + "  "
        recursion_depth = recursion_depth -1
    print(tabs_init + input_file + " to file " + output_filename)

def find_links(markdown_content):
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, markdown_content)

    # for link in links:
    #     print(f"Link text: {link[0]}")
    #     print(f"URL: {link[1]}")

    files = [link[1] for link in links]

    return files


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Usage python3 epub_creator.py entrypoint_file.md")
        exit (1)
    entrypoint_file = sys.argv[1]
    # entrypoint_file = 'documentation.md'  # Replace with the actual filename
    output_file = entrypoint_file + ".epub"

    added_links = []

    convert_markdown_to_epub(entrypoint_file, 
                             output_file, 
                             1,
                             added_links)

