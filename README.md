## Supportutils Plugin pmem

This is a support utils plugin to gather information on ndctl (NVDIMM) & ipmctl (Intel pmem) 
tools for issue diagnosis.

To test:

    sudo LOG=/tmp python3 ./pmem.py

The cmd above will output pmem log data to /tmp/pmem.txt.

Information about Intel Optane persistent memory modules (pmem):

https://github.com/intel/ipmctl

Information about Manage "libnvdimm" subsystem devices (Non-volatile Memory):

https://www.suse.com/c/nvdimm-enabling-suse-linux-enterprise-12-service-pack-2/

https://www.suse.com/c/nvdimm-enabling-part-2-intel/

https://documentation.suse.com/sles/15-SP3/html/SLES-all/cha-nvdimm.html

https://github.com/pmem/ndctl