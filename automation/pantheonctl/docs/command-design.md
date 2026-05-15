# pantheonctl Command Design

## Status

status: scaffold

## Design Rules

- Commands begin as read-only or generate-only.
- Commands must show what external tool they would call before future orchestration is introduced.
- Mutating infrastructure commands are deferred.
- Package dependencies are not added until a command needs them and the reason is documented here.

## Deferred Commands

- `pantheonctl apply`
- `pantheonctl deploy`
- `pantheonctl firewall modify`
- `pantheonctl switch configure`
- `pantheonctl atlas shares modify`
- `pantheonctl secrets rotate`
- `pantheonctl terraform apply`
- `pantheonctl pulumi up`
- `pantheonctl ansible run`
