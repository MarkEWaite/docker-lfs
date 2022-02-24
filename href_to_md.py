#!/usr/bin/env python

# Convert href links to markdown links

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
            if 'a href=' not in content:
                # print("File: " + file_name + " contains no markdown link")
                continue
            print("File: " + file_name + " contains an href link")
            m = re.search('&lt;a href=&quot;(.*?)&quot;&gt;(.*?)&lt;/a&gt;', content)
            if m:
                link_text = m.group(1)
                link_url = m.group(2)
                print("search result:", link_text, link_url)
            replaced_content = re.sub('&lt;a href=&quot;(.*?)&quot;&gt;(.*?)&lt;/a&gt;',
                                      '[\\2](\\1)',
                                      content)
        with open(file_name, 'w') as file_content:
            file_content.write(replaced_content)

#-----------------------------------------------------------------------

if __name__ == "__main__": md_to_href(sys.argv[1:])
