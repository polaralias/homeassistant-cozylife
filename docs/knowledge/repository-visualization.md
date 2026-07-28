---
type: Visualization
title: "homeassistant-cozylife repository OKF visualization"
description: "Defines the source, scope, outputs, interpretation, and verification contract for the repository-wide OKF visualization."
timestamp: 2026-07-28T22:56:13Z
authority: derived
verification: verified-working
owner: polaralias
generated_by: repo-task-lifecycle-visualizer
tags: [homeassistant-cozylife, visualization]
navigation: {role: supporting, order: 40}
---

# homeassistant-cozylife repository OKF visualization

## Source and scope

The repository root is the visualization bundle. Skill-package trees and the generated Mermaid report are excluded by [the persisted view policy](../../.okf-visualization-ignore).

## Outputs

- [Interactive HTML workspace](../visualizations/repository-okf.html)
- [Scalable Mermaid report](../visualizations/repository-okf.mermaid.md)

## Interpretation

The generated Graph, Board, and Reader views are derived navigation aids. Repository Markdown and YAML records remain authoritative.

## Verification

Regenerate both outputs with the repository-task visualizer and run its freshness check after meaningful record or renderer changes.

## Related knowledge

- [Documentation map](./documentation-map.md)
- [Documentation inventory](./documentation-inventory.md)
- [RKE OKF adoption task](../../tasks/adopt-rke-okf-knowledge/task.md)
