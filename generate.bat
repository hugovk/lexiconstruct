call python lexiconstruct.py -n 2 > a-dictionary-of-not-a-words.md

call timeit pandoc -s -c style.css -T "A Dictionary of Not-A-Words" a-dictionary-of-not-a-words.md -o a-dictionary-of-not-a-words.html

call a-dictionary-of-not-a-words.html

call pandoc --latex-engine=xelatex -c style.css -T "A Dictionary of Not-A-Words" a-dictionary-of-not-a-words.md -o a-dictionary-of-not-a-words.pdf

call a-dictionary-of-not-a-words.pdf

