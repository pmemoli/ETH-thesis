## Hypervisor

A hypervisor is a type of computer software, firmware, or hardware that creates and runs Virtual Machines by *virtualizing hardware*. The computer on which the hypervisor runs is called a host machine, and each VM is called a guest machine. 

Type 1 hypervisors access and administer the physical resources directly, while Type 2 hypervisors run as userspace programs that negotiate resource allocation with the OS.

In the KVM context, the hypervisor is the kernel space functionality and the VMM the userspace functionality (say QEMU or Firecracker).

## KVM

KVM is a linux kernel module that allows the kernel to act as a type 1 hypervisor. MicroVMs tend to be implemented with KVM for running the instructions in native hardware, where a each workload has its own dedicated kernel.

## Firecracker

Firecracker is a VMM built on top of the linux KVM. It is minimalistic by design, exposing a small set of devices to the microVMs (network interface, storage device, serial console and minimal keyboard controller). The syscalls available to the VMM are also minimalistic through a jailer process.

It works over a rest API over a unix socket, providing an openAPI documentation.

## Containers

OS level virtualization or Containerization is the use of the native OS interface to run applications in separate userspaces (named containers), thereby virtualizing the entire OS for the application. 

The most common technology for implementing containers is Docker, where the templates are defined docker images.
