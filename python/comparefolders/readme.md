# CompareFolders

### What is this?
It's a tool made for... you guessed it! Comparing folders!

### Usage
py comparefolders.py {args}

| Argument | Syntax | Usage |
| :----: | :---: | :--- |
| (any path) | "path/to/folder" | Adds the given path for comparing (must be a folder path.) |
| -i (name)  | -i "*.pyc" | Ignores folders and files with the name provided. | 
| -m (mode)  | -m "compare/fetch/dir" | Changes the operation mode [ compare: Standard comparation / fetch: Copies all different files / dir: Doesn't compare at all, just returns all existing paths. ] |
| -o (name) | -o "compare.log" | Defines the file the output is gonna get written at. Can be set to nothing to prevent an output. |
| -s         | -s | Enables silent mode (doesn't display different files and ends silently.) |
| -n         | -n | Clears all given paths / ignore names (mainly used when borrowing the script.) |
#### You can also specify these args within the script itself for frequent usage.