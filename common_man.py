#!/usr/bin/env python3
import subprocess
import re
from collections import Counter
import matplotlib.pyplot as plt

def search_manpages(programs):
    options = []
    for program in programs:
        try:
            manpage = subprocess.check_output(["man", program]).decode()
            program_options = re.findall(r'(?<!\\)-{1,2}[\w-]+', manpage)
            options.extend(program_options)
        except subprocess.CalledProcessError:
            print(f"Error: Could not find manpage for {program}")
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

# Example usage
programs = ['ls', 'grep', 'cat', 'cp', 'mv']  # Add more programs as needed
options = search_manpages(programs)
create_histogram(options, top_n=10)
