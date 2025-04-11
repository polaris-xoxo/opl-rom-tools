## Why
I got fed up with OPL Manager's wonky rename function and decided to write my own script for it.

## Usage
Copy the script to your rom storage folder and run the following command in a terminal of your choice.
```
python opl-rom-tools.py [options]
```
## Options
| Option   | Effect |
|----------| ------ |
| -v / --v | verbose output |
| -h / --h | display help message |

## How does it work?
The script attempts to extract the game serial from each iso file and looks it up on [Redump](http://redump.org).
After that it renames each file to *&lt;game serial&gt;*.*&lt;game name&gt;*.iso.

## What now
I might add cover art downloading / copying at some point if I feel like it, not sure yet.

## This code sucks lmao!
Probably, i barely ever touch python.