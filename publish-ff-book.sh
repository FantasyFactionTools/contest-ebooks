#!/bin/bash

# this script will ask you for the location of, and then pull/copy/commit/push
# the final book files from the build-ff-books.sh script.
#
# use from the scripts directory:
#	./publish-ff-book.sh
#
# it'll ask you questions.
#

echo ""
echo "--------------------------------------------------------------------------------------------------"
echo "NOTE: if you've made any strange updates to the tools site, please do a merge!"
echo ""


# save our current directory.
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"


# where are we putting the output files?
read -p "Where is your local copy of FantasyFactionTools.github.io? (../FantasyFactionTools.github.io/): " RESP
DIR="../FantasyFactionTools.github.io/"
if [ "$RESP" != "" ]
then
	DIR="$RESP"
fi
cd "${DIR}"


# make sure the repo is ready for a deploy.
# we should probably do more than just this.
echo "Updating git repo."
git pull


# dumping all the books into the website repo
echo "moving books to publish directory."
NEWLINE=$'\n'
LOGDUMP="==========================================================="
LOGDUMP="$LOGDUMP"$'\n'"[i]kindle mobi:[/i]"
for i in ${SCRIPT_DIR}/output/*; do
    if [ "${i}" != "${i%.mobi}" ];then
        mv "${i}" "writing-contest"
        filename=$(basename "${i}")
        LOGDUMP="$LOGDUMP"$'\n'"https://fantasyfactiontools.github.io/writing-contest/$filename"
    fi
done
LOGDUMP="$LOGDUMP"$'\n'

LOGDUMP="$LOGDUMP"$'\n'"[i]generic epub:[/i]"
for i in ${SCRIPT_DIR}/output/*; do
    if [ "${i}" != "${i%.epub}" ];then
        mv "${i}" "writing-contest"
        filename=$(basename "${i}")
        LOGDUMP="$LOGDUMP"$'\n'"https://fantasyfactiontools.github.io/writing-contest/$filename"
    fi
done
LOGDUMP="$LOGDUMP"$'\n'

LOGDUMP="$LOGDUMP"$'\n'"[i]word document:[/i]"
for i in ${SCRIPT_DIR}/output/*; do
    if [ "${i}" != "${i%.docx}" ];then
        mv "${i}" "writing-contest"
        filename=$(basename "${i}")
        LOGDUMP="$LOGDUMP"$'\n'"https://fantasyfactiontools.github.io/writing-contest/$filename"
    fi
done
LOGDUMP="$LOGDUMP"$'\n'

LOGDUMP="$LOGDUMP"$'\n'"[i]critique sheet:[/i]"
for i in ${SCRIPT_DIR}/critiques/*; do
    if [ "${i}" != "${i%.md}" ];then
        mv "${i}" "writing-contest"
        filename=$(basename "${i}")
        LOGDUMP="$LOGDUMP"$'\n'"https://fantasyfactiontools.github.io/writing-contest/$filename"
    fi
done

LOGDUMP="$LOGDUMP"$'\n'
LOGDUMP="$LOGDUMP"$'\n'"NOTE: Files with '-noauthor' appended only have the author"
LOGDUMP="$LOGDUMP"$'\n'"names listed at the beginning, on the table of contents."
LOGDUMP="$LOGDUMP"$'\n'"==========================================================="


# deploying.
echo "committing and pushing the git repo live."
git add .
git commit -m "pushing new writing contest ebooks."
git push


# and, done!
echo "finished."
echo ""
printf "%s\n" "$LOGDUMP"

exit 0


# grab everything
python contest-grabber.py

#exit 0

# load in the generated conf
source ebook.conf


# build the ebook cover.

imagename=$(basename "${ImageUrl}")
wget "${ImageUrl}"

convert $imagename cover.jpg
rm $imagename

test=`convert cover.jpg -format "%[fx:(w/h>1)?1:0]" info:`
if [ $test -eq 1 ]; then
echo "Extra-wide Image"
sips --resampleHeight 1250 cover.jpg
else
echo "Extra-tall Image"
sips --resampleWidth 1250 cover.jpg
fi

# 750x1250 (3x5 ratio)
sips --cropToHeightWidth 1250 750 cover.jpg -o cover.jpg

# apply best fit text to: x90y900 w600h260
convert -background linen -bordercolor linen -border 10x10 -fill OrangeRed4 -gravity center -font LibreBaskervilleB -size 600x180 caption:"${Title}" title.jpg
convert -background linen -bordercolor linen -border 10x20 -fill grey24 -gravity center -font LibreBaskervilleB -size 600x60 caption:"${Subtitle}" subtitle.jpg

composite -geometry +60+900 title.jpg cover.jpg cover.jpg
composite -geometry +60+1070 subtitle.jpg cover.jpg cover.jpg


#exit 0


# make the epub and mobi.
ebook-convert "output/${ShortTitle}.html" "output/${ShortTitle}.epub" --cover="cover.jpg" --authors="${Author}" --series="${Series}" --title="${Title}" --level1-toc="//h:h1" --use-auto-toc --chapter-mark=both --output-profile=ipad
ebook-convert "output/${ShortTitle}.html" "output/${ShortTitle}.mobi" --cover="cover.jpg" --authors="${Author}" --series="${Series}" --title="${Title}" --level1-toc="//h:h1" --use-auto-toc --chapter-mark=both --output-profile=kindle
#ebook-convert "output/${ShortTitle}.html" "output/${ShortTitle}.rtf" --cover="cover.jpg" --authors="${Author}" --series="${Series}" --title="${Title}" --level1-toc="//h:h1" --use-auto-toc --chapter-mark=both 
pandoc -s "output/${ShortTitle}-rtf.html" -o "output/${ShortTitle}.docx"


#exit 0

# move the critique file to its spot.
mv "critiques-${ShortTitle}.md" critiques

# push the ebook files
scp "output/${ShortTitle}.epub" m3mnoch@chapmanholdings.com:/var/www/www.m3mnoch.com/static/ff-books/
scp "output/${ShortTitle}.mobi" m3mnoch@chapmanholdings.com:/var/www/www.m3mnoch.com/static/ff-books/
scp "output/${ShortTitle}.docx" m3mnoch@chapmanholdings.com:/var/www/www.m3mnoch.com/static/ff-books/
scp "output/${ShortTitle}.html" m3mnoch@chapmanholdings.com:/var/www/www.m3mnoch.com/static/ff-books/
scp "cover.jpg" m3mnoch@chapmanholdings.com:/var/www/www.m3mnoch.com/static/ff-books/covers/${ShortTitle}-cover.jpg


if [ $ShowAuthor -eq 0 ]; then
echo ""
echo ""
echo "=================================================================="
echo "- [b]Authors only on Table of Contents[/b] -"
echo "[i]generic epub:[/i]"
echo "http://m3mnoch.com/static/ff-books/${ShortTitle}.epub"
echo ""
echo "[i]kindle mobi:[/i]"
echo "http://m3mnoch.com/static/ff-books/${ShortTitle}.mobi"
echo ""
echo "[i]word document:[/i]"
echo "http://m3mnoch.com/static/ff-books/${ShortTitle}.docx"
echo "=================================================================="
else
echo "=================================================================="
echo "- [b]Authors on Each Story[/b] -"
echo "[i]generic epub:[/i]"
echo "http://m3mnoch.com/static/ff-books/${ShortTitle}.epub"
echo ""
echo "[i]kindle mobi:[/i]"
echo "http://m3mnoch.com/static/ff-books/${ShortTitle}.mobi"
echo ""
echo "[i]word document:[/i]"
echo "http://m3mnoch.com/static/ff-books/${ShortTitle}.docx"
echo "=================================================================="
fi
