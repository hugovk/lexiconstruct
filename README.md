lexiconstruct
=============

Create a dictionary from archived tweets.

    python lexiconstruct.py -n 2 > a-dictionary-of-not-a-words.md

    pandoc -s -c style.css a-dictionary-of-not-a-words.md -o a-dictionary-of-not-a-words.html

Windows:

    pandoc --latex-engine=xelatex -c style.css -T "A Dictionary of Not-A-Words" a-dictionary-of-not-a-words.md -o a-dictionary-of-not-a-words.pdf

See also:

 * http://johnmacfarlane.net/pandoc/installing.html
