# Split file

### Info

Split one file into several files given command line arguments.

**Reading and writing occurs line by line.**

Arguments:
* ```-h``` show this help message and exit;
* one option to select, title line does not count:
  * ```-l n``` create output files with **n** lines, the last file may contain fewer lines;
  * ```-f n``` create **n** files, the difference in the number of lines in these files is no more than one;
* ```-e``` encoding of source file and output files;
* ```-t``` include title (first line of the source file) in output files;
* ```-v``` display created output files;
* ```source_file``` file name or full path to the file that will be split;
* ```target_dir ``` directory of output files (default: dir source_file), the files will have the same name, extension, encoding, but a new numbering suffix.

---

### Prerequisites

Language version starting from Python 3.10+

```bash
$ python --version
Python 3.10.4
```

---

### Usage

```bash
$ python split_file.py -h
usage: split_file.py [-h] (-l NLINES | -f NFILES) [-e ENCODING] [-t] [-v] source_file [target_dir]

description:
    Split one file into several files given command line arguments.
    New files are created with a sequence number suffix.
    New files are not created if there are no lines to create them.
    Warning: new files may erase old files!

positional arguments:
  source_file           file name or full path file
  target_dir            directory of output files (default: dir source_file)

options:
  -h, --help            show this help message and exit
  -l NLINES, --nlines NLINES
                        number of lines in output files
  -f NFILES, --nfiles NFILES
                        number of output files
  -e ENCODING, --encoding ENCODING
                        encoding of source file and output files
  -t, --title           include title (first line of the source file) in output files
  -v, --verbose         display created output files
```

```bash
$ cat temp/input.csv
0
1
2
3
4
5
6
```

```bash
$ python split_file.py -l 4 -t -v temp/input.csv
start...
temp\input_1.csv
temp\input_2.csv
success!

$ cat temp/input_1.csv
0
1
2
3
4

$ cat temp/input_2.csv
0
5
6
```

```bash
$ python split_file.py -f 3 -v temp/input.csv
start...
temp\input_1.csv
temp\input_2.csv
temp\input_3.csv
success!

$ cat temp/input_1.csv
0
1
2

$ cat temp/input_2.csv
3
4

$ cat temp/input_3.csv
5
6
```

---

### Authors

* [Dmitry Volkov](https://github.com/d1mav0lk0v)

---

### Link

* [GitHub](https://github.com/d1mav0lk0v/split_file)

---