#!/usr/bin/sh

# This is the overall kernel for the project

# Step 1: Run kernel

#./execute sos.ipynb
#./execute statewides.ipynb

# Step 2: Convert to HTML

python -m tohtml sos.ipynb html/sos.html
python -m tohtml statewides.ipynb html/statewides.html

# Step 3: Upload to website