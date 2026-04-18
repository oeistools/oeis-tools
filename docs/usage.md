# Usage Guide

This guide covers the core functionalities of `oeis-tools` with practical examples.

## Plotting Data

You can quickly plot sequence data using the built-in matplotlib integration in the `BFile` class. This is particularly useful for observing the behavior of integer sequences visually.

### Example: Plotting a Single Sequence

```python
import matplotlib.pyplot as plt
from oeis_tools import BFile

# Fetch the Fibonacci sequence b-file
bfile = BFile("A000045")

# Plot the first 80 points using a scatter plot
bfile.plot_data(80, plot_style="scatter", color="black")
```

### Example: Overlaying Sequences

You can use the `ax` parameter to overlay multiple sequences on the same matplotlib axes.

```python
import matplotlib.pyplot as plt
from oeis_tools import BFile

N_POINTS = 200

bfile1 = BFile("A114906")
bfile2 = BFile("A114904")

fig, ax = plt.subplots()

# Plot first sequence in red without showing the figure yet
bfile1.plot_data(n=N_POINTS, ax=ax, show=False, color="red")

# Plot second sequence in blue and show the figure
bfile2.plot_data(n=N_POINTS, ax=ax, show=True, color="blue")
```

## Retrieving Metadata

The `Sequence` class fetches the extensive metadata provided by the OEIS JSON API.

```python
from oeis_tools import Sequence

seq = Sequence("A000045")

print(f"ID: {seq.id}")
print(f"Name: {seq.name}")
print(f"Author: {seq.author}")
print(f"Keywords: {seq.keyword}")

# Get the first few terms of the sequence
print(f"Data: {seq.data[:10]}")
```

## Creating Custom B-Files

If you generate an OEIS sequence locally, you can create a compliant b-file using `create_bfile`.

```python
from oeis_tools.bfile import create_bfile

my_sequence = [1, 2, 3, 5, 8, 13]
# Generates b213676.txt in the current directory starting from n=1
create_bfile("A213676", my_sequence, offset=1)
```
