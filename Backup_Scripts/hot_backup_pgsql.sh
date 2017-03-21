#!/usr/bin/env bash
# Backup Values
    export BACKUP_HOST="159.203.178.175" #Change it According to use
    export BACKUP_BASE_DIR="/data/dailybackups/"
    export BACKUP_WEEK_DIR="/data/weeklybackup/"
    export PROJECT_NAME='ShortDate' # Change it As a project name
    export NOW=`date +%Y_%m_%d-%H_%M_%S`
    export BACKUP_DIR=$BACKUP_BASE_DIR/$NOW

# Backup
    mkdir -p $BACKUP_BASE_DIR
    mkdir -p $BACKUP_WEEK_DIR
    rm -rf $BACKUP_BASE_DIR/*

    mkdir -p $BACKUP_DIR
    chown -R postgres.postgres $BACKUP_DIR
    chmod -R 700 $BACKUP_DIR
    echo "Permission Granted on Data Directory!"

    #Create backup
    sudo -u postgres pg_basebackup -P -X stream -c fast -h 127.0.0.1 -D $BACKUP_DIR

    #Compression
    cd $BACKUP_BASE_DIR
    TARGET=$BACKUP_WEEK_DIR/$NOW.tar.gz
    SOURCE=$NOW
    tar -zcvf $TARGET $SOURCE 2>>/dev/null 1>>/dev/null

    # Send File to Backup Server
    ssh -o StrictHostKeyChecking=no root@$BACKUP_HOST "mkdir -p /data/$PROJECT_NAME/$HOSTNAME"
    scp -o StrictHostKeyChecking=no $TARGET root@$BACKUP_HOST:/data/$PROJECT_NAME/$HOSTNAME/

    # Cleaning Server
    find $BACKUP_WEEK_DIR/* -mtime +7 -exec rm -rf {} \;
    ssh -o StrictHostKeyChecking=no root@$BACKUP_HOST "find /data/$PROJECT_NAME/$HOSTNAME/* -mtime +7 -exec rm -rf {} \;"

    echo "backup completed!!"