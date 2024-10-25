import re

# Read the dataset from a file
with open('./BrillioDataset/test-dataset 1.csv', 'r') as file:
    lines = file.readlines()

# Initialize variables to store cleaned data
cleaned_lines = lines[:1]
current_line = ''
current_line_idx=1

# Process each line
for line in lines[1:-1]:
    # Check if the line starts with a number
    if line.startswith(f"{current_line_idx},"):
        # If a new line starts with a number, save the current line and start a new one
        cleaned_lines.append(current_line.strip())
        current_line = line.strip()
        current_line_idx+=1
    else:
        # If the line does not start with a number, append it to the current line
        current_line += ' ' + line.strip()

# Append the last accumulated line
if current_line:
    cleaned_lines.append(current_line.strip())

# Write the cleaned lines to a new file
with open('./BrillioDataset/test-dataset_clean.csv', 'w') as file:
    for line in cleaned_lines:
        file.write(line + '\n')

print(f"Newlines removed. Cleaned dataset saved . Concatenated")
