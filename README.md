## contest-ebooks
Python and Bash scripts to build ebooks from the Fantasy Faction Monthly Contest

#### pip install Pre-requisites
- Requests
- PyQuery
- Markdown
- um...  maybe more?  update me when you install from scratch, please!

#### brew install Pre-requisites (sorry! you non-OSX people will have to figure this one out on your own)
- calibre
- pandoc
- imagemagick

(I should probably just write a shell script that installs all of the pre-requisites)

## The Basics
This is how you go about publishing the ebooks for the writing contest community.

#### Building the ebooks
1. Change to the directory where this repo is located.
1. Run the Bash script to build the book. ```$: ./build-ff-book.sh```
1. It will then ask you some questions.
    1. Are you building the version with authors on each story? ```Show the authors? (y/n):```
    1. Have you already pulled down the HTML from the forums and stored it in local cache? ```Use existing cache? (y/n):```
    1. What is the URL for the submissions page? ```What is the submissions URL?:```
    1. What is the URL for the voting page?  (It pulls official title/authors from there) ```What is the voting URL?:```
1. Then, it grinds through, building the various ebook versions, and storing them in the _output_ directory

#### Publishing the ebooks
1. Run the Bash script to publish the ebook versions. ```$: ./publish-ff-book.sh```
1. It will then ask you the location of your local copy of the Fantasy Faction Tools website repository. ```Where is your local copy of FantasyFactionTools.github.io? (../FantasyFactionTools.github.io/):```
1. Afterwards, it copys/commits/pushes the changes to hosting site
1. And, finally, prints a handy bit of code to copy/paste into a post for everyone in the forums.

```
===========================================================
[i]kindle mobi:[/i]
https://fantasyfactiontools.github.io/writing-contest/random-wikipedia-article-noauthor.mobi
https://fantasyfactiontools.github.io/writing-contest/random-wikipedia-article.mobi

[i]generic epub:[/i]
https://fantasyfactiontools.github.io/writing-contest/random-wikipedia-article-noauthor.epub
https://fantasyfactiontools.github.io/writing-contest/random-wikipedia-article.epub

[i]word document:[/i]
https://fantasyfactiontools.github.io/writing-contest/random-wikipedia-article-noauthor.docx
https://fantasyfactiontools.github.io/writing-contest/random-wikipedia-article.docx

[i]critique sheet:[/i]
https://fantasyfactiontools.github.io/writing-contest/critiques-random-wikipedia-article.md

NOTE: Files with '-noauthor' appended only have the author
names listed at the beginning, on the table of contents.
===========================================================
```