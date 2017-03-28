#!/usr/bin/env bash

# Setup Values
col='"'
export PERCONA_USER="webops"
export HOST='localhost'
export PERCONA_PASS=`date +%s | sha256sum | base64 | head -c 20 ; echo`
export PERCONA_MYSQL_PASS=`date +%s | sha384sum | base64 | head -c 20 ; echo`
export MYSQL_ROOT_PASS=""


# Backup Values
export BACKUP_HOST="159.203.178.175" #Change it According to use
export BACKUP_USER="root"
export BACKUP_PASS=""
export BACKUP_BASE_DIR='/data'
export PROJECT_NAME='Abbott' # Change it As a project name
export PERCONA_MYSQL_USERPASS='123'
NOW=`date +%Y_%m_%d-%H_%M_%S`




ESC_SEQ="\x1b["
RESET=$ESC_SEQ"39;49;00m"
FAILED=$ESC_SEQ"31;01m"
SUCCESS=$ESC_SEQ"32;01m"
WARNING=$ESC_SEQ"33;01m"
INFO=$ESC_SEQ"34;01m"




install_percona_backup(){
    # Download Repo
    wget https://repo.percona.com/apt/percona-release_0.1-4.$(lsb_release -sc)_all.deb 1>>/dev/null 2>>/dev/null
    STAT_REPO_DNLD="$?"
    if [ ! $STAT_REPO_DNLD -eq 0 ]; then
        echo "Failed Repo Download!"
        exit 1
    else
        echo "Repo Downloaded!"
    fi

    # Install Repo
    sudo dpkg -i percona-release_0.1-4.$(lsb_release -sc)_all.deb 1>>/dev/null 2>>/dev/null
    STAT_REPO_INSTALL="$?"
    if [ ! $STAT_REPO_INSTALL -eq 0 ]; then
        echo "Failed Repo Installation !"
        exit 1
    else
        echo "Repo Installed!"
        rm -rf percona-release_0.1-4.$(lsb_release -sc)_all.deb 1>>/dev/null 2>>/dev/null
    fi

    # Update Repo
    sudo apt-get update 1>>/dev/null 2>>/dev/null
    STAT_REPO_UPDATE="$?"
    if [ ! $STAT_REPO_UPDATE -eq 0 ]; then
        echo "Failed Repo Update !"
        exit 1
    else
        echo "Repo Updateed!"
    fi

    # Install Percona
    sudo apt-get install -y percona-xtrabackup 1>>/dev/null 2>>/dev/null
    STAT_PERCONA_INSTALL="$?"
    if [ ! $STAT_PERCONA_INSTALL -eq 0 ]; then
        echo "Failed Percona Install !"
        exit 1
    fi

    echo "Percona Xtrabackup Installed Successfully"
}

question_root_password_for_backup_server(){
read -p "Please Root Password for Backup Server: " BACKUP_PASS
sshpass -p $BACKUP_PASS ssh -o StrictHostKeyChecking=no $BACKUP_USER@$BACKUP_HOST "exit"
AUTH=$?
if [ ! $AUTH -eq 0 ]; then
    echo "ERROR '${AUTH}': Authentication Failed Please Try Again!"
    question_root_password_for_backup_server
fi
}

system_configure_percona_backup(){
    # Add/Configure Webops System User
    echo "Configuring System for Percona..."
    apt-get install -y sshpass 1>>/dev/null 2>>/dev/null
    mkdir -p /var/www
    useradd $PERCONA_USER
    usermod -s /bin/bash -d /var/www/ $PERCONA_USER
    #usermod -p $(echo $PERCONA_PASS | openssl passwd -1 -stdin) $PERCONA_USER
    echo "$PERCONA_USER ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers;
    if [ $? -eq 0 ]; then
        echo "System User $PERCONA_USER is Ready with Password $PERCONA_PASS"
    else
        echo "Failed to set Password of System User $PERCONA_USER"
    fi
    usermod -aG sudo $PERCONA_USER
    gpasswd -a $PERCONA_USER mysql
    chown -R $PERCONA_USER: /data

    # Auth Setting
    question_root_password_for_backup_server
    echo "y"|ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa 1>>/dev/null 2>>/dev/null
    cat ~/.ssh/id_rsa.pub | sshpass -p $BACKUP_PASS ssh -o StrictHostKeyChecking=no $BACKUP_USER@$BACKUP_HOST "mkdir -p ~/.ssh/; cat >> ~/.ssh/authorized_keys; chmod -R 600 ~/.ssh/"

    if [ ! $? -eq 0 ]; then
        echo "Auth Setup Failed!"
        echo "Please setup Manually Password-less SSH Authentication"
    else
        echo "Auth Setup Done!"
    fi
}

mysql_root_login_check(){
    # Add/Configure webops Mysql User
    read -p "Please Enter Mysql Root Password: " MYSQL_ROOT_PASS
    mysql -u root -p$MYSQL_ROOT_PASS -e exit 2>/dev/null
    STAT_ROOT_LOGIN="$?"
    if [ ! $STAT_ROOT_LOGIN -eq 0 ]; then
        echo "Failed Mysql Root Login Try Again!"
        mysql_root_login_check
    fi
}

question_existing_user_password(){
    read -p "Please Enter Mysql Password for $PERCONA_USER: " EXIST_USER_PASS
    mysql -u $PERCONA_USER -p$EXIST_USER_PASS -e exit 2>/dev/null
    if [ ! $? -eq 0 ]; then
        echo "Failed Mysql $PERCONA_USER Login, Try Again !"
        question_existing_user_password
    fi
    PERCONA_MYSQL_PASS=$EXIST_USER_PASS
}

mysql_configure_percona_backup(){
    echo "Configuring Mysql for Percona..."
    if [[ ! -z "`mysql -u root -p$MYSQL_ROOT_PASS -qfsBe "SELECT User FROM mysql.user where User=$col$PERCONA_USER$col" 2>&1`" ]]; then
        echo ""
        echo "User $PERCONA_USER Already Exist"
        echo "1. Reset Password"
        echo "2. Use Existing Password"
        read -p "Please Select Options Given Above [1/2]: " EXIST_USER_OPTION

        if [ $EXIST_USER_OPTION -eq 1 ]; then
            mysql -u root -p$MYSQL_ROOT_PASS -e "UPDATE mysql.user SET Password=PASSWORD('${PERCONA_MYSQL_PASS}') WHERE User='${PERCONA_USER}'" 2>>/dev/null
            if [ ! $? -eq 0 ]; then
                mysql -u root -p$MYSQL_ROOT_PASS -e "UPDATE mysql.user SET authentication_string=PASSWORD('${PERCONA_MYSQL_PASS}') WHERE User='${PERCONA_USER}'" 2>>/dev/null
                if [ ! $? -eq 0 ]; then
                    echo "Password Update for $PERCONA_USER Failed in 2nd Try!"
                else
                    echo "Password of $PERCONA_USER is reset to $PERCONA_MYSQL_PASS"
                fi
            else
                echo "Password of $PERCONA_USER is reset to $PERCONA_MYSQL_PASS"
            fi
        elif [ $EXIST_USER_OPTION -eq 2 ]; then
            question_existing_user_password
            mysql -u root -p$MYSQL_ROOT_PASS -e "UPDATE mysql.user SET authentication_string=PASSWORD('${PERCONA_MYSQL_PASS}') WHERE User='${PERCONA_USER}'" 2>>/dev/null
            if [ $? -eq 0 ]; then
                echo "Mysql User $PERCONA_USER has been Updated with Password $PERCONA_MYSQL_PASS"
            else
                echo "Failed to Reset Password for Mysql User $PERCONA_USER"
            fi
        else
            mysql_configure_percona_backup
        fi
    else
        mysql -u root -p$MYSQL_ROOT_PASS -e "CREATE USER '${PERCONA_USER}'@'${HOST}' IDENTIFIED BY '${PERCONA_MYSQL_PASS}'" 2>/dev/null
        echo "New Mysql User $PERCONA_USER Created with Password $PERCONA_MYSQL_PASS"
    fi
    mysql -u root -p$MYSQL_ROOT_PASS -e "GRANT RELOAD, LOCK TABLES, REPLICATION CLIENT ON *.* to '${PERCONA_USER}'@'${HOST}';"
    mysql -u root -p$MYSQL_ROOT_PASS -e "FLUSH PRIVILEGES;"
}

take_backup(){
    mkdir -p /data/dailybackups/
    mkdir -p /data/weeklybackup/
    rm -rf /data/dailybackups/*
    sudo chown -R mysql: /var/lib/mysql
    sudo find /var/lib/mysql -type d -exec chmod 770 "{}" \;
    echo "Permission Granted on Data Directory!"

    #Create backup
    innobackupex --user=$PERCONA_USER --password=$PERCONA_MYSQL_USERPASS --no-timestamp /data/dailybackups/$NOW

    #Prepare backup
    innobackupex --apply-log /data/dailybackups/$NOW

    #Compression
    cd /data/dailybackups/
    TARGET=/data/weeklybackup/$NOW.tar.gz
    SOURCE=$NOW
    tar -zcvf $TARGET $SOURCE 2>>/dev/null 1>>/dev/null

    # Send File to Backup Server
    ssh -o StrictHostKeyChecking=no root@$BACKUP_HOST "mkdir -p /data/$PROJECT_NAME/$HOSTNAME"
    scp -o StrictHostKeyChecking=no $TARGET root@$BACKUP_HOST:/data/$PROJECT_NAME/$HOSTNAME/

    # Cleaning Server
    find /data/weeklybackup/* -mtime +7 -exec rm -rf {} \;
    ssh -o StrictHostKeyChecking=no root@$BACKUP_HOST "find /data/$PROJECT_NAME/$HOSTNAME/* -mtime +7 -exec rm -rf {} \;"

    echo "backup completed!!"

}

setup(){
    install_percona_backup
    system_configure_percona_backup
    mysql_root_login_check
    mysql_configure_percona_backup

    echo "Setup Completed with Details Below"
    echo -e "System User username: ${INFO}$PERCONA_USER${RESET}"
    echo -e "System User password: ${INFO}$PERCONA_PASS ${RESET}"
    echo -e "Mysql User username: ${INFO}$PERCONA_USER${RESET}"
    echo -e "Mysql User password: ${INFO}$PERCONA_MYSQL_PASS ${RESET}"
}

backup(){
    take_backup
}


case "$1" in
"setup")
    setup
    ;;
"backup")
    backup
    ;;
"")
    echo "ERROR: No Argument Provided!"
    echo "Script Usage:"
    echo "      to setup: <script name> setup"
    echo "      to backup: <script name> backup"
    echo "Example"
    echo "      ./parcona_synapse.sh setup"
    echo "      ./parcona_synapse.sh backup"
    ;;
*)
    echo "ERROR: Invalid Argument '${1}'"
    echo "Script Usage:"
    echo "      to setup: <script name> setup"
    echo "      to backup: <script name> backup"
    echo "Example"
    echo "      ./parcona_synapse.sh setup"
    echo "      ./parcona_synapse.sh backup"
    ;;
esac