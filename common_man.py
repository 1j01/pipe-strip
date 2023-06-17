#!/usr/bin/env python3
import subprocess
import re
from collections import Counter
import matplotlib.pyplot as plt

def get_all_installed_programs():
    try:
        dpkg_output = subprocess.check_output(["dpkg", "--list"]).decode()
        installed_programs = re.findall(r'ii\s+([\w+-]+)', dpkg_output)
        return installed_programs
    except subprocess.CalledProcessError:
        print("Error: Failed to retrieve the list of installed programs.")
        return []

def search_manpages(programs):
    options = []
    for program in programs:
        try:
            manpage = subprocess.check_output(["man", program]).decode()
            program_options = re.findall(r'(?<!\\)-{1,2}[\w-]+', manpage)
            options.extend(program_options)
        except subprocess.CalledProcessError:
            pass  # Ignore programs without manpages
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

# Get the list of installed programs
installed_programs = get_all_installed_programs()

# Search manpages for options
options = search_manpages(installed_programs)

# Create histogram of the most common options
create_histogram(options, top_n=10)
