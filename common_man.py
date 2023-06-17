#!/usr/bin/env python3
import os
import re
import gzip
from collections import Counter
import plotly.graph_objects as go
import glob

def search_manpages(manpages_dir):
    options = []
    file_paths = []
    pattern = os.path.join(manpages_dir, 'man*')
    for dirpath in glob.glob(pattern):
        for root, _, filenames in os.walk(dirpath):
            for filename in filenames:
                if filename.endswith('.gz'):
                    manpage_path = os.path.join(root, filename)
                    try:
                        with gzip.open(manpage_path, 'rt', encoding='utf-8', errors='replace') as manpage_file:
                            manpage_text = manpage_file.read()
                            assert isinstance(manpage_text, str)
                            program_options = re.findall(r'^(?:\s*)(?<!\\)-{1,2}[\w-]+(?<!-)', manpage_text, re.MULTILINE)
                            options.extend(program_options)
                            file_paths.extend([manpage_path] * len(program_options))
                            print(f"Found {len(program_options)} options in {manpage_path}: {program_options!r}")
                    except IOError:
                        print(f"Error: Failed to read manpage at {manpage_path}")
                    except UnicodeDecodeError:
                        print(f"Error: Failed to decode manpage at {manpage_path}")
    return options, file_paths

def create_histogram(options, file_paths, top_n=10):
    option_counts = Counter(options)
    most_common = option_counts.most_common(top_n)
    
    x = [option[0] for option in most_common]
    y = [option[1] for option in most_common]
    
    hover_text = [f"Option: {option}<br>Frequency: {count}<br>Files:<br>{'<br>'.join(file_paths[i] for i, opt in enumerate(options) if opt == option)}" for option, count in most_common]
    
    fig = go.Figure(data=[go.Bar(x=x, y=y, hovertext=hover_text)])
    
    fig.update_layout(
        title=f"Top {top_n} Most Common Options",
        xaxis_title="Options",
        yaxis_title="Frequency",
        xaxis=dict(tickangle=45),
        hovermode="x"
    )
    
    fig.show()

# Specify the manpages directory
manpages_dir = '/usr/share/man'  # Modify this as per your system's manpages directory

# Search manpages for options and file paths
options, file_paths = search_manpages(manpages_dir)

# Create histogram of the most common options with file paths
create_histogram(options, file_paths, top_n=10)
