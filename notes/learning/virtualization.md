## Hypervisor

A hypervisor is a type of computer software, firmware, or hardware that creates and runs Virtual Machines by *virtualizing hardware*. The computer on which the hypervisor runs is called a host machine, and each VM is called a guest machine. 

Type 1 hypervisors access and administer the physical resources directly, while Type 2 hypervisors run as userspace programs that negotiate resource allocation with the OS.

In the KVM context, the hypervisor is the kernel space functionality and the VMM the userspace functionality (say QEMU).

## KVM

KVM is a linux kernel module that allows the kernel to act as a type 1 hypervisor.

TODO: Read a bit more on device io syscalls, kinda forgot about it lol. I want to understand the section How does KVM work? in [here](https://northflank.com/blog/what-is-kvm).
