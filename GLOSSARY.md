# Glossary

This glossary defines the product-language and support-language used by this repository.

The goal is to keep public claims precise while the integration moves from inherited behaviour towards verified support.

## Language

**Verified supported surface**:
A user-visible integration surface that has been validated on real hardware to the repository's chosen evidence bar and can be claimed publicly.
_Avoid_: supported enough, probably supported, assumed support

**Partially supported surface**:
A device surface that is verified on real hardware for some but not all expected controls or behaviours in its class.
_Avoid_: supported enough, mostly supported

**Available code path**:
A behaviour implemented in the repository but not yet validated or supported as a public contract.
_Avoid_: supported feature, planned support

**Potentially supported surface**:
A device class that the repository can plausibly classify or operate from catalogue data, but that has not yet been verified on real hardware.
_Avoid_: supported surface, maintained support

**Catalogue snapshot**:
A checked-in local copy of upstream device metadata used for classification and capability inference.
_Avoid_: support matrix, verified device list

**Capability parity target**:
The feature set the repository should aim to match when the provider-level catalogue declares those capabilities for a device model.
_Avoid_: guaranteed support, assumed runtime truth

**Model/PID truth unit**:
The concrete device model identifier used as the primary unit for support and parity decisions.
_Avoid_: class-only support truth

**Light-class device**:
A CozyLife device treated as a Home Assistant light by the integration.
_Avoid_: bulb feature, lighting path

**Switch-class device**:
A CozyLife device treated as a switch-related surface by the integration code.
_Avoid_: supported switch, verified switch

**Sensor-class device**:
A CozyLife device exposed through sensor-related code paths in the integration.
_Avoid_: supported sensor, verified sensor

## Relationships

- A **Verified supported surface** may be backed by one or more **Available code paths**
- A **Potentially supported surface** may be inferred from catalogue data without being a **Verified supported surface**
- A **Catalogue snapshot** can widen the set of **Potentially supported surfaces** without widening the **Verified supported surface**
- A **Partially supported surface** is narrower than a **Verified supported surface** but stronger than a **Potentially supported surface**
- A **Light-class device** is currently the only **Verified supported surface**
- **Switch-class device** and **Sensor-class device** behaviour currently exist as **Available code paths** and **Potentially supported surfaces**
- A **Light-class device** should not be created by re-wrapping a **Switch-class device** as a light entity
- A **Verified supported surface** for this repository currently requires discovery, query, and successful control of the relevant device features on at least one real device in that class
- Live device behaviour determines support truth, while the **Catalogue snapshot** defines the closest provider-level **Capability parity target**
- Support and parity decisions should be tracked first at the **Model/PID truth unit**, then summarised upward by class if patterns emerge

## Example dialogue

> **Dev:** "Do we support switches?"
> **Domain expert:** "Not as a first-class supported surface — switches are an **Available code path** and a **Potentially supported surface**, but only lights are a **Verified supported surface** right now."

## Flagged ambiguities

- "supported" was being used to mean both "exists in code" and "verified on hardware" — resolved: only the latter counts as a **Verified supported surface**
- "probably working" was being used as if it were support status — resolved: that maps to **Potentially supported surface**, not **Verified supported surface**
- "light surface" was being used both for actual light-capable devices and for compatibility wrappers around switches — resolved: light surfaces are reserved for actual **Light-class devices**
- `model.json` could be mistaken for a support declaration — resolved: it is a **Catalogue snapshot**
- "supported" versus "partially supported" was underdefined — resolved: partial support means the device works on real hardware but not all expected controls for that class are verified working
- Live capability truth and catalogue-declared capability truth could be conflated — resolved: live behaviour decides support status, and catalogue data defines the parity target and mismatch record
