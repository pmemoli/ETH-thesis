"""Profile for running agentic benchmark experiments using AgentENV as the environment.

A RawPC is used since a real /dev/kvm is needed to run firecracker.
"""

import geni.portal as portal
import geni.rspec.pg as rspec

DEFAULT_IMAGE = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD"

# Define build-time params
pc = portal.context

pc.defineParameter(
    "phystype",
    "Hardware type",
    portal.ParameterType.NODETYPE,
    "",
    longDescription="Leave blank to let the mapper pick whatever is free.",
)

params = pc.bindParameters()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Create a raw PC
node = request.RawPC("node")
node.disk_image = DEFAULT_IMAGE

# Install dependencies
node.addService(
    rspec.Execute(shell="bash", command="/local/repository/profile.sh")
)

# Write the request in RSpec format
portal.context.printRequestRSpec()
