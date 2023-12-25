import os
import re
import sys
import subprocess

# @brief convert_markdown_to_epub
#        Convert input file to just one epub.
#
# @param input_file      [in]    Input file. Beware the function is recursive
#
# @return Exit code.
def convert_markdown_to_epub(input_file):
    added_links = []
    contents = ""
    recursion_depth = 1

    contents = read_metadata()

    contents = recurse_files(input_file, recursion_depth, added_links, contents)

    output_filename = get_output_filename(input_file)

    print_recursion(recursion_depth, input_file, output_filename)


    # Convert the current Markdown file to EPUB
    # if recursion_depth == 1:
    write_files(contents, output_filename)

##
# @brief recurse_files Iterate recursively through the files.
#
# @param input_file [in] Input file
# @param recursion_depth [in] Recursion depth as a number
# @param added_links [in] As md is not structured take into accaount links that are already added
# @param contents [in] Contents are being passed then recreated.
#
# @return Contents with links substitued by the link content.
def recurse_files(input_file, recursion_depth, added_links, contents):
    # Read the Markdown file
    # print("Read markdown file: " + input_file)
    with open(input_file, 'r') as f:
        markdown_content = f.read()

    # print("Adding to contents file " + input_file)
    contents = contents + "\n\n" + markdown_content

    # Find links and print them.
    links = find_links(markdown_content)

    # Convert linked Markdown files recursively
    for link in links:
        # print (link)
        # linked_file = os.path.join(os.path.dirname(input_file), str(link))
        linked_file = find_file(input_file, str(link))
        # print ("linked_file " + linked_file)

        already_added = added_links.count(linked_file) > 0
        if already_added:
            # print ("already added: " + linked_file)
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
    output_filename = output_filename.replace(" ", "_")
    return output_filename

def write_files(content, output_file):

    #Replace images for it's true path.
    content = process_images(content)

    print("Write also markdown to file: result_markdown.md")
    g = open("result_markdown.md", "wt")
    g.write(content)
    g.close()


    print("Finally creating the file:")
    cmd = "pandoc --verbose --css=./epub.css {} -o {}".format("result_markdown.md", output_file)
    os.system(cmd)
    print(cmd)


# Substitute routes for images. Taking into account that we are in the current directory, it must
# search for the images in the subdirectories, then use the correct path.
def process_images(content):
    images = find_images(content)

    for img in images:
        basename = os.path.basename(img)
        dirname  = os.path.dirname(img)
        cmd = "find . -path '*{}*{}'".format(dirname, basename)
        print("Find command to execute: " + cmd)
        os.system(cmd)
        # find_output = subprocess.check_output(cmd, shell=True)
        find_output = subprocess.run(cmd, shell=True, capture_output=True)

        #If returning 0, replace link to image.
        if not find_output.returncode:
            output = find_output.stdout.decode("utf-8")
            content = content.replace(img, output)
            print("Replacing {} with {}".format(img, output))

    #Seems that I'm forced to flush the output here, else the messages appear unordered.
    sys.stdout.flush()
    sys.stderr.flush()

    return content

def find_file(input_file, linked_file):

    file_path = ""
    basename = os.path.basename(linked_file)
    dirname  = os.path.dirname(linked_file)
    if dirname:
        cmd = "find . -path '*{}*{}'".format(dirname, basename)
    else:
        cmd = "find . -path '{}'".format(basename)
    print("Find command to execute: " + cmd)
    os.system(cmd)
    # find_output = subprocess.check_output(cmd, shell=True)
    find_output = subprocess.run(cmd, shell=True, capture_output=True)

    #If returning 0, replace link to image.
    if not find_output.returncode:
      output = find_output.stdout.decode("utf-8")
      if output:
        file_path = linked_file.replace(linked_file, output)
        file_path = file_path[2:]
        file_path = os.path.join(os.path.dirname(input_file), linked_file)
        # print("Replacing {} with {}".format(linked_file, file_path))
      else:
        file_path = os.path.join(os.path.dirname(input_file), linked_file)

    #Seems that I'm forced to flush the output here, else the messages appear unordered.
    sys.stdout.flush()
    sys.stderr.flush()

    return file_path



def find_links(markdown_content):
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, markdown_content)

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


    return images

def read_metadata():
    metadata = ""
    with open("metadata_header.txt", 'r') as f:
        metadata = f.read()

    return metadata




if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Usage python3 epub_creator.py entrypoint_file.md")
        exit (1)
    entrypoint_file = sys.argv[1]


    convert_markdown_to_epub(entrypoint_file)

