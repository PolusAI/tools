class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/optional_scatter_wf.cwl
inputs:
- id: optional_scatter_wf___0__step__uppercase2_wic_compatible2_optional___message
  type: string[]
outputs:
- id: optional_scatter_wf___0__step__uppercase2_wic_compatible2_optional___uppercase_message
  outputSource: 0__step__uppercase2_wic_compatible2_optional/uppercase_message
  type: string[]
requirements:
- class: ScatterFeatureRequirement
steps:
- id: 0__step__uppercase2_wic_compatible2_optional
  in:
  - id: message
    source: optional_scatter_wf___0__step__uppercase2_wic_compatible2_optional___message
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible2_optional.cwl
  scatter:
  - message
  - uppercase_message
  scatterMethod: !!python/object/apply:polus.tools.workflows.model.ScatterMethodEnum
  - dotproduct
