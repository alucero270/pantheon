ADR 0001: Zero-Trust Lite Network Model

Status: Accepted

Context

The network model for the homelab needs to ensure that no implicit trust exists between VLANs. This is essential to limit lateral movement in case of a compromise, ensuring that devices in one VLAN cannot access the resources of another VLAN without explicit permission.

Decision

The homelab will use a Zero-Trust Lite model, which involves:

Explicit access permissions between VLANs

No direct communication between VLANs unless configured

Every connection and communication path must be explicitly defined

Consequences

Increased rule complexity in the firewall configuration

Stronger security posture and separation of concerns

The need for careful firewall management to avoid misconfigurations
