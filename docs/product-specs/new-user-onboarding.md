# New User Onboarding

## Desired User Outcome

A user should be able to install the integration and discover verified supported CozyLife devices without editing YAML or reverse-engineering network details first.

## Expected Flow

1. User installs the custom component.
2. User adds the integration from Home Assistant.
3. The integration derives likely local subnets automatically.
4. The integration scans automatically unless the user provides a manual range.
5. The user selects discovered devices.
6. The user confirms names and areas.
7. Home Assistant creates the expected entities.

## Current Verified Elements

- config flow exists and is the intended onboarding route,
- automatic range derivation is implemented,
- manual IP-range input is implemented,
- live broadcast-assisted discovery has been validated with a real bulb,
- automated tests now cover IP-only import probing into a canonical single-device entry shape.

## Current Unknowns

- the exact onboarding experience for switches on real hardware,
- how intuitive the entity outcome is for mixed device classes,
- whether all legacy config-entry paths are still worth preserving.

## Current Support Policy

- lights are the only verified supported onboarding target,
- switches and sensors may appear through existing code paths but are not yet supported or tested without contributor validation.
