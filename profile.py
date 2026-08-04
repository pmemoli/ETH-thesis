"""Profile for running agentic benchmark experiments using AgentENV as the environment.

A RawPC is used since a real /dev/kvm is needed to run firecracker.
"""

import geni.portal as portal
import geni.rspec.pg as rspec

DEFAULT_IMAGE = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD"
HARDWARE_TYPE = "r6525"

# Create a Request object to start building the RSpec.
request = portal.context.makeRequestRSpec()

# Create a raw PC
node = request.RawPC("node")

node.disk_image = DEFAULT_IMAGE
node.hardware_type = HARDWARE_TYPE

# Write the request in RSpec format
portal.context.printRequestRSpec()
