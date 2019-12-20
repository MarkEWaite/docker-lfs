#!/usr/bin/env python

# Convert markdown links to href links

import os
import re
import subprocess
import sys

#-----------------------------------------------------------------------

def md_to_href(args):
    "Convert markdown links to href links in XML files"
    for file_name in args:
        # print("File: " + file_name)
        with open(file_name, 'r') as file_content:
            content = file_content.read()
            if '](' not in content:
                # print("File: " + file_name + " contains no markdown link")
                continue
            print("File: " + file_name + " contains a markdown link")
            m = re.search('\[(.+)\]\((.+)\)', content)
            if m:
                link_text = m.group(1)
                link_url = m.group(2)
                print("search:", link_text, link_url)
            replaced_content = re.sub('\[([^\]]+)\]\(([^)]+)\)',
                                      '&lt;a href=&quot;\\2&quot;&gt;\\1&lt;/a&gt;',
                                      content)
        with open(file_name, 'w') as file_content:
            file_content.write(replaced_content)

#-----------------------------------------------------------------------

if __name__ == "__main__": md_to_href(sys.argv[1:])
