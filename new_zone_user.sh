#!/bin/bash

#
# Create a new user on an OpenSolaris system
#

# check for command line parameter
if [ -z "$1" ]; then 
   echo usage: $0 new_user
   exit
fi

USER_NAME=$1
USER_HOME=/export/home/$USER_NAME

echo $USER_NAME
echo $USER_HOME

/usr/bin/mkdir $USER_HOME
/usr/sbin/useradd -d $USER_HOME -s /bin/bash $USER_NAME
/usr/bin/chown $USER_NAME $USER_HOME
/usr/bin/chgrp other $USER_HOME
/usr/bin/chmod 755 $USER_HOME
/usr/bin/cp /root/.fetchmailrc $USER_HOME
/usr/bin/cp /root/.procmailrc $USER_HOME
/usr/bin/chown new_user $USER_HOME/.fetchmailrc
/usr/bin/chown new_user $USER_HOME/.procmailrc
/usr/bin/chmod 710 $USER_HOME/.fetchmailrc
/usr/bin/chmod 744 $USER_HOME/.procmailrc

