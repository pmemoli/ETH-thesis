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

## AgentENV

[AgentENV](https://github.com/kvcache-ai/AgentENV) is the self-hosted sandbox runtime we'll use for the AI agents. It runs firecracker microVMs and exposes an E2B-compatible HTTP API which is what the harnesses will use to interact with the VMs. 

There are 3 ways of interacting with the aenv process, through the aenv CLI, and the E2B-compatible HTTP API. Since there is an e2b sdk, we can just spawn stuff within it programatically.

## E2B

[E2B](https://github.com/e2b-dev/e2b) is an infrastructure that allows for running AI-generated code in a sanboxed environment in the cloud. The sandbox is interfaced through a REST API, and it provides an official SDK that can interact with any E2B compatible endpoint.
