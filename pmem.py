#!/usr/bin/python3
# Plugin for suse supportconfig support tool.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.
import mimetypes
import os
import subprocess
import sys
from io import IOBase
from pathlib import Path
import re

# to run
#   LOG=/tmp python3 pmem.py

ENV_HDR = "#==[ Env ]======================================#\n"
COMMAND_HDR = "#==[ Command ]======================================#\n"
CFG_HDR = "#==[ Configuration File ]===========================#\n"
LOG_HDR = "#==[ Log File ]=====================================#\n"
NOTE_HDR = "#==[ Note ]=========================================#\n"
SUMMARY_HDR = "#==[ Summary ]======================================#\n"
ENTRY_HDR = "#==[ Entry ]========================================#\n"
ERROR_HDR = "#==[ ERROR ]========================================#\n"
FSI_HDR = "#==[ File System Information ]========================================#\n"

BINARY_ATTR = ['ndctl', 'daxctl']
PKGS = ['ndctl', 'libndctl6', 'ipmctl']
SERVICE = ['ndctl-monitor']

CFG = [
    "/etc/ndctl",
    "/etc/ipmctl.conf",
    "/etc/ndctl/monitor.conf"
    ]

LOGS = [
    "/var/log/ipmctl",
    "/var/log/ndctl"
    ]

CMDS = [
    ['ndctl', '--version'],
    ['ndctl', 'list', '-vvv'],
    ['ndctl', 'list', '-iBDFHMNRX'],
    ['ndctl', 'read-labels', '-j', 'all'],
    ['daxctl', 'list'],
    ['daxctl', 'list', '-iDR'],
    ['ipmctl', 'version'],
    ['ipmctl', 'show', '-cap'],
    ['ipmctl', 'show', '-cel'],
    ['ipmctl', 'show', '-dimm'],
    ['ipmctl', 'show', '-a', '-dimm'],
    ['ipmctl', 'show', '-dimm', '-pcd'],
    ['ipmctl', 'show', '-dimm', '-performance'],
    ['ipmctl', 'show', '-error', 'Thermal', '-dimm'],
    ['ipmctl', 'show', '-error', 'Media', '-dimm'],
    ['ipmctl', 'show', '-firmware'],
    ['ipmctl', 'show', '-goal'],
    ['ipmctl', 'show', '-memoryresources'],
    ['ipmctl', 'show', '-performance'],
    ['ipmctl', 'show', '-preferences'],
    ['ipmctl', 'show', '-region'],
    ['ipmctl', 'show', '-sensor'],
    ['ipmctl', 'show', '-a', '-sensor'],
    ['ipmctl', 'show', '-socket'],
    ['ipmctl', 'show', '-system'],
    ['ipmctl', 'show', '-system', '-capabilities'],
    ['ipmctl', 'show', '-a', '-system', '-capabilities'],
    ['ipmctl', 'show', '-topology'],
    ['ipmctl', 'show', '-a', '-topology']
    ]

# MOUNTS = ['/usr/bin/mount', '| egrep', '^/dev/pmem[0-9]+'] #, 'awk', '{print $1 $3}' ]
MOUNTS = ['/usr/bin/mount']
PMEM_TESTSTRING = ['/dev/sda7 / ext4 rw,relatime 0 0', '/dev/sdb1 /home xfs rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota 0 0', '/dev/pmem2 /hana/pmem/nv03 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem1 /hana/pmem/nv02 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem12 /hana/pmem/nv13 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem9 /hana/pmem/nv10 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem13 /hana/pmem/nv14 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem4 /hana/pmem/nv05 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem3 /hana/pmem/nv04 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem8 /hana/pmem/nv09 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem0 /hana/pmem/nv01 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem6 /hana/pmem/nv07 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem14 /hana/pmem/nv15 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem7 /hana/pmem/nv08 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem5 /hana/pmem/nv06 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem15 /hana/pmem/nv16 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem10 /hana/pmem/nv11 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0', '/dev/pmem11 /hana/pmem/nv12 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0' ]

DEBUG = False

def log_data(logfile, hdr, msgs):
    logfile.write(hdr)
    # don't save empty or comment lines
    if type(msgs) == str:
        logfile.write("%s\n" % msgs)
    else:
        for msg in msgs:
            if len(msg) != 0 and not msg.startswith('#'):
                logfile.write("%s\n" % msg)
    logfile.write("\n")

def run_cmd(cmd, check, shell=False):
    output = subprocess.run(
            cmd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=shell
        )
    if output.stderr:
        raise subprocess.CalledProcessError(
                returncode = output.returncode,
                cmd = output.args,
                stderr = output.stderr
                )

    if output.stdout:
        return output.stdout.decode('UTF-8')
    return ''

def log_env(logfile):
    logfile.write(ENV_HDR)
    for k, v in sorted(os.environ.items()):
        logfile.write("{0}: {1}\n".format(k, v))
    logfile.write("\n")

def log_cmd(logfile: object, cmd: object, check: object = True, shell: object = False) -> object:
    logfile.write(COMMAND_HDR)
    logfile.write("%s\n" % " ".join(cmd))
    status = True
    try:
        if shell:
            cmd = " ".join(cmd)
            output = run_cmd(cmd, check, shell)
        else:
            output = run_cmd(cmd, check, shell)
        logfile.write(output)
    except Exception as e:
        # logfile.write("ERROR: subprocess raised error: {}\n".format(e))
        status = False
    logfile.write("\n")
    return status

def rpm_verify(logfile):
    # If there are changes this gives a 1 returncode, but we don't care.
    for p in PKGS:
        log_cmd(logfile, ["rpm", "-V", p], check=False)

def service_check(logfile, inst_name):
    log_cmd(logfile, ["systemctl", "status", inst_name], check=False)
    log_cmd(logfile, ["ls", "-alhH",
                      "/etc/systemd/system/{0}.service.d".format(inst_name)], check=False)
    try:
        # Can we display the content of this dir?
        if os.path.exists("/etc/systemd/system/{0}.service.d".format(inst_name)):
            for cnf in os.listdir("/etc/systemd/system/{0}.service.d".format(inst_name)):
                p = os.path.join("/etc/systemd/system/{0}.service.d".format(inst_name), cnf)
                dump_log_config(logfile, COMMAND_HDR, p)
    except Exception as e:
        # Probably no overrides.
        log_data(logfile, ERROR_HDR, e)

def service_check_logs(logfile, inst_name):
    log_cmd(logfile, ["journalctl", "-u", inst_name, "-p", "5"], check=False)

def dump_log_config(logfile, hdr, path):
    if hdr == LOG_HDR:
        prefix = ""
    else:
        prefix = "config -> "
    if os.path.exists(path):
        with open(path, 'r') as cnf_f:
            log_data(logfile, hdr, ["{0}{1}:".format(prefix, path)] + [x.replace('\n', '') for x in cnf_f.readlines()])
    else:
        log_data(logfile, ERROR_HDR, "No such file/dir: {0}".format(path))

def dump_log_config_traverse(logfile, hdr, path):
    if os.path.exists(path):
        if os.path.isdir(path):
            for file in path.iterdir():
                if file.is_dir():
                    dump_log_config_traverse(logfile, hdr, file)
                else:
                    mime_type, encoding = mimetypes.guess_type("{0}".format(file))
                    if DEBUG:
                        print("DEBUG: file: {0} Type: {1}".format(file, encoding))

                    # skip compressed files
                    types_mapping = mimetypes.types_map
                    if encoding in mimetypes.encodings_map.values() or \
                            encoding in list(types_mapping.keys()):
                        continue
                    dump_log_config(logfile, hdr, file)
    else:
        log_data(logfile, ERROR_HDR, "No such file/dir: {0}".format(path))

def run_cmds(logfile, check=True, shell=False):
    for c in CMDS:
        log_cmd(logfile, c, check, shell)

def mount_info(logfile):
    output = run_cmd(MOUNTS, check=True)
#   COMMENT THIS OUT BEFORE PKGING
    # print(output)
    pattern = '^/dev/pmem[0-9]+'
    pattern2 = '^/dev/sd[a-z]+[0-9]+'
    # expected input
    # /dev/pmem12 /hana/pmem/nv13 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0
    cmdsout = ''
# COMMENT THIS OUT BEFORE PKGING
    # for l in output:
    # output = PMEM_TESTSTRING
    for l in output.splitlines():
        cmd = []
        match = re.search(pattern, l)
        match2 = re.search(pattern2, l)
        if match or match2:
            pstr = l.split(' ')
            fs = pstr[2]
            dev = pstr[0]
            if fs == 'xfs':
                cmd.append('/usr/sbin/xfs_info')
                cmd.append(dev)
            elif fs == 'ext4':
                cmd.append('/sbin/dumpe2fs')
                cmd.append('-h')
                cmd.append(dev)
            else:
                continue
        if cmd:
            cmdstr = ''
            for cmdelm in cmd:
                cmdstr = cmdstr + cmdelm + ' '
            try:
                s = run_cmd(cmd, check=True)
                cmdsout = cmdsout + cmdstr + '\n' + s + '\n'
            except subprocess.CalledProcessError as e:
                # cmdstr = '{0} {1}: '.format(cmd[0], cmd[1])
                # replace double '\n' for pp output
                outstr = str((e.output).decode('utf-8')).replace('\n\n','\n\t')
                cmdsout = cmdsout + cmdstr + '\n' + outstr
                pass

    if cmdsout:
        log_data(logfile, FSI_HDR, cmdsout)

def xfsio_pmem_info(logfile):
    output = run_cmd(MOUNTS, check=True)
#   COMMENT THIS OUT BEFORE PKGING
    # print(output)
    pattern = '^/dev/pmem[0-9]+'
    # expected input
    # /dev/pmem12 /hana/pmem/nv13 xfs rw,relatime,attr2,dax,inode64,sunit=4096,swidth=4096,noquota 0 0
    cmdsout = ''
# COMMENT THIS OUT BEFORE PKGING
    output = PMEM_TESTSTRING
    #    for l in output.splitlines():
    for l in output:
        cmd = []
        match = re.search(pattern, l)
        if match:
            pstr = l.split(' ')
            fs = pstr[2]
            dev = pstr[0]
            if fs == 'xfs':
                cmd.append('/usr/sbin/xfs_io')
                cmd.append('-c')
                cmd.append('\'extsize\'')
                cmd.append(dev)
            else:
                continue
        if cmd:
            cmdstr = ''
            for cmdelm in cmd:
                cmdstr = cmdstr + cmdelm + ' '
            try:
                s = run_cmd(cmd, check=True)
                cmdsout = cmdsout + cmdstr + '\n' + s + '\n'
            except subprocess.CalledProcessError as e:
                # cmdstr = '{0} {1}: '.format(cmd[0], cmd[1])
                # replace double '\n' for pp output
                outstr = str((e.output).decode('utf-8')).replace('\n\n','\n\t')
                cmdsout = cmdsout + cmdstr + '\n' + outstr
                pass

    if cmdsout:
        log_data(logfile, FSI_HDR, cmdsout)

def do_supportconfig():
    # Get our logfile name
    logfilename = os.path.join(os.environ['LOG'], 'pmem.txt')
    # Start to write some stuff out.
    with open(logfilename, 'w', encoding='utf-8') as logfile:
        if not log_cmd(logfile, ["rpm", "-q", PKGS[0]]):
            logfile.close()
            os.remove(logfilename)
            sys.exit(0)

        if DEBUG:
            log_env(logfile)

        # Do the rpm verification to proceed
        rpm_verify(logfile)

        # Run through cmd list
        run_cmds(logfile)

        mount_info(logfile)
        xfsio_pmem_info(logfile)

        # Display configuration.
        for p in CFG:
            if os.path.isdir(p):
                myPath = Path(p)
                dump_log_config_traverse(logfile, CFG_HDR, myPath)
            else:
               dump_log_config(logfile, CFG_HDR, p)

        # Check service
        for s in SERVICE:
            service_check(logfile, s)
            service_check_logs(logfile, s)

        # Display Logfiles.
        for p in LOGS:
            if os.path.isdir(p):
                myPath = Path(p)
                dump_log_config_traverse(logfile, LOG_HDR, myPath)
            else:
                dump_log_config(logfile, LOG_HDR, p)

if __name__ == "__main__":
    do_supportconfig()

# vim: set et ts=4 sw=4 :
