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
