#!/usr/bin/bash

log_dir="/tmp"

while [ ! -e ${DBUS_SESSION_BUS_ADDRESS##*=} ]; do
    echo "Waiting for session bus (${DBUS_SESSION_BUS_ADDRESS}) to become available."
    sleep 1;
done
# capture traffic on the session bus for debugging purposes
dbus-monitor --pcap > "${log_dir}/dbus.pcap" &

# check if a core dump for a PID exists and if not, create it
check_dump_pid() {
    local pid="$1"
    if [ ! -f ${log_dir}/dump-${pid}-*.info ]; then
        # find corresponding executable name and replace slashes
        local exe=$(coredumpctl --no-legend | awk -v pid=" *${pid} *" '
            $5 ~ pid {
                gsub("/", "-", $10)
                print $10
            }
        ')
        local dump_prefix="${log_dir}/dump-${pid}-${exe}"
        coredumpctl info ${pid} &> "${dump_prefix}.info"

        # upload the core dump to FTP (due to file size constraint in Beaker),
        # we can just make use of the existing compressed core dump
        local existing_dump=$(awk '/Storage:/ {print $2}' ${dump_prefix}.info)
        existing_dump=${existing_dump/ /}
        local dump_ext="${existing_dump##*.}"
        local recipeid="$(cat /run/anabot/recipeid)"
        local upload_filename="dump-${recipeid}-${pid}-${exe}.${dump_ext}"
        if [[ -f /run/anabot/ftp_server && -f /run/anabot/ftp_user && \
            -f /run/anabot/ftp_password ]]; then
            local ftp_server=$(cat /run/anabot/ftp_server)
            local ftp_user=$(cat /run/anabot/ftp_user)
            local ftp_password=$(cat /run/anabot/ftp_password)
            ftp -npv ${ftp_server} <<< "
                user ${ftp_user} ${ftp_password}
                put ${existing_dump} ${upload_filename}"
        else
            echo "Not uploading core dump for '${existing_dump}', FTP server settings \n
are missing or incomplete!"
        fi
    fi
}

# have a look for possible core dumps (should be uploaded by Anabot,
# together with the dbus traffic capture)
old_dump_pids=""
while sleep 1; do
    # coredumpctl output may also contain unwanted output (besides the core dump
    # records) under some circumstances, so we need to make sure to only filter the PIDs
    new_dump_pids=$(coredumpctl --no-legend | awk '$5 ~ "^ *[0-9]+ *$" {print $5}')
    if [ "${new_dump_pids}" != "${old_dump_pids}" ]; then
        echo "old_dump_pids: '$old_dump_pids'; new_dump_pids: '$new_dump_pids'"
        for pid in ${new_dump_pids}; do
            check_dump_pid ${pid}
        done
        old_dump_pids="${new_dump_pids}"
    fi
done
