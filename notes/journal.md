# Journal

## July 31, 2026

Today I'm formally starting my master thesis. Pre-start notes are found in `pre_start.md`. 

The main goal right now is connecting to ETH's computers, creating scripts to sync easily and setting up a minimal agent environment. As discussed with Cedric and Xiao, this environment will be Kimi 3's [Agent ENV](https://github.com/kvcache-ai/AgentENV). In parallel, I would like to read on the technical aspects of Firecracker's VMs, and Kimi 3.

I succesfully connected to the destination ${USER}@${DOMAIN_NAME} and synced it with mutagen to my local machine.

I've also read upon hypervisors and the KVM through:

- [Hypervisor](https://en.wikipedia.org/wiki/Hypervisor)
- [KVM](https://northflank.com/blog/what-is-kvm)

And a bunch of other resources. Super interesting.

On monday I'm going to finish reading on Firecracker, KVMs and general device I/O which i kinda forgot about. After that I want to setup a Firecracker instance and then some 4B model running its context on Agent ENV.
