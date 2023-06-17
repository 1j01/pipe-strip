#!/usr/bin/env python3
import os
import re
import gzip
from collections import Counter
import matplotlib.pyplot as plt

def search_manpages(manpages_dir):
    options = []
    for root, _, files in os.walk(manpages_dir):
        for file in files:
            if file.endswith('.gz'):
                manpage_path = os.path.join(root, file)
                try:
                    with gzip.open(manpage_path, 'rt', encoding='utf-8', errors='replace') as manpage_file:
                        manpage_text = manpage_file.read()
                        program_options = re.findall(r'^(?:\s*)(?<!\\)-{1,2}[\w-]+(?<!-)', manpage_text, re.MULTILINE)
                        options.extend(program_options)
                        print(f"Found {len(program_options)} options in {manpage_path}: {program_options!r}")
                except IOError:
                    print(f"Error: Failed to read manpage at {manpage_path}")
                except UnicodeDecodeError:
                    print(f"Error: Failed to decode manpage at {manpage_path}")
    return options

def create_histogram(options, top_n=10):
    option_counts = Counter(options)
    most_common = option_counts.most_common(top_n)
    
    x = [option[0] for option in most_common]
    y = [option[1] for option in most_common]
    
    plt.bar(x, y)
    plt.xlabel('Options')
    plt.ylabel('Frequency')
    plt.title(f'Top {top_n} Most Common Options')
    plt.xticks(rotation=45)
    plt.show()

# Specify the manpages directory
manpages_dir = '/usr/share/man'  # Modify this as per your system's manpages directory

# Search manpages for options
options = search_manpages(manpages_dir)

# Create histogram of the most common options
create_histogram(options, top_n=10)
