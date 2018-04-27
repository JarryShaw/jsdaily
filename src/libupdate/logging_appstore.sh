#!/bin/bash


# clear potential terminal buffer
sript -q /dev/null tput clear > /dev/null 2>&1


################################################################################
# Log App Store packages updates.
#
# Parameter List
#   1. Log File
#   2. Temp File
################################################################################


# parameter assignment
logfile=$1
tmpfile=$2


# remove /tmp/log/update.log
rm -f "$tmpfile"


# create /tmp/log/update.log & /Library/Logs/Scripts/update/logdate/logtime.log
touch "$logfile"
touch "$tmpfile"


# log current status
echo "- /bin/bash $0 $@" >> "$tmpfile"


# log commands
logprefix="script -aq "$tmpfile""
# logsuffix="grep ^.*$"


# check for oudated packages
echo -e "+ softwareupdate --list | sed \"s/-$//\" | grep -e \"*\" | sed \"s/.*\* \(.*\)*[-].*/\1/\"" >> "$tmpfile"
$logprefix softwareupdate --list | sed "s/-$//" | grep -e "*" | sed "s/.*\* \(.*\)*[-].*/\1/"
echo >> "$tmpfile"


# aftermath works
bash ./libupdate/aftermath.sh "$logfile" "$tmpfile"


# remove /tmp/log/update.log
rm -f "$tmpfile"


# clear potential terminal buffer
sript -q /dev/null tput clear > /dev/null 2>&1
