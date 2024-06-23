import os
import re
from collections import defaultdict


def generate_output(temp_string, app_name):
    with open(app_name, 'w') as file:
        # Write the string to the file
        file.write(temp_string)


# Directory containing the files
directory_path = 'puppet_module/files'

# Initialize dictionaries to store grouped filenames
normal_scripts = defaultdict(list)
complex_scripts = defaultdict(list)

# Regular expression to match the filename pattern
pattern = re.compile(r"^(pre|post)-deploy-(\w+)-(\w+)-(\d+)\.sh$")

# Temporary dictionary to store all files
all_files = defaultdict(list)

# Iterate through each file in the directory
for filename in os.listdir(directory_path):
    match = pattern.match(filename)
    if match:
        prefix, word2, app_name, number = match.groups()
        number = int(number)
        # Remove the .sh extension
        filename_without_ext = os.path.splitext(filename)[0]
        all_files[app_name].append((filename_without_ext, number))

# Separate files into normal and complex scripts
for app_name, files in all_files.items():
    has_complex = any(number != 1 for _, number in files)
    if has_complex:
        for filename_without_ext, number in files:
            complex_scripts[app_name].append(filename_without_ext)
    else:
        for filename_without_ext, number in files:
            normal_scripts[app_name].append(filename_without_ext)

# Convert the defaultdict to a regular dictionary for easier handling
normal_scripts = dict(normal_scripts)
complex_scripts = dict(complex_scripts)

template_string = """file {
  default:
    ensure => file,
    mode   => '0600',
    owner  => 'root',
    group  => 'root',

pre xxxxxx
post yyyyy
  }"""

template_string_2 = """file {
  default:
    ensure => file,
    mode   => '0600',
    owner  => 'root',
    group  => 'root',

common zzzz 
  }"""

# Output the grouped filenames
print("Normal Scripts:")
for app_name, files in normal_scripts.items():
    print(f"{app_name}: {files}")
    if len(normal_scripts.get(app_name)):
        pre_list = [i for i in normal_scripts.get(app_name) if 'pre' in str(i)]
        post_list = [i for i in normal_scripts.get(app_name) if 'post' in str(i)]
        output_string = template_string.replace('xxxxxx', pre_list[0]) if len(pre_list) else template_string.replace(
            'pre xxxxxx', '')
        output_string = output_string.replace('yyyyy', post_list[0]) if len(post_list) else output_string.replace(
            'post yyyyy', '')
        generate_output(output_string, f'{app_name}.pp')
print("\nComplex Scripts:")
for app_name, files in complex_scripts.items():
    print(f"{app_name}: {files}")
    if len(complex_scripts.get(app_name)):
        app_list = complex_scripts.get(app_name)
        pre_list = [i for i in complex_scripts.get(app_name) if 'pre' in str(i)]
        post_list = [i for i in complex_scripts.get(app_name) if 'post' in str(i)]
        output_string = template_string.replace('xxxxxx', pre_list[-1])
        app_list.remove(pre_list[-1])
        output_string = output_string.replace('yyyyy', post_list[0])
        app_list.remove(post_list[0])
        generate_output(output_string, f'{app_name}_.pp')

        for remaining in app_list:
            output_string_2 = template_string_2.replace('zzzz', remaining)
            generate_output(output_string_2, f'{app_name}_{remaining}.pp')