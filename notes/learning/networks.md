## SSH auth

[Source](https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys)

SSH (secure shell) is a secure protocol for connecting to remote linux servers. It is implemented through a client-server model, where the remote machine runs an SSH daemon that listens for connections on a specific port, and the user has an SSH client which knows how to communicate using the protocol.

One way to connect is with encrypted passwords which is easy but unsafe. Another is by having a pair of keys (public/private), which is the more secure option. These are generated with ssh-keygen and can be copied with ssh-copy-id
