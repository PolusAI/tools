class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/test_workflow_builder/wf4.cwl
inputs:
- id: wf4___0__step__wf3___wf3___0__step__echo_string___message
  type: string
outputs:
- id: wf4___0__step__wf3___wf3___0__step__echo_string___message_string
  outputSource: 0__step__wf3/wf3___0__step__echo_string___message_string
  type: string
- id: wf4___0__step__wf3___wf3___1__step__uppercase2_wic_compatible2___uppercase_message
  outputSource: 0__step__wf3/wf3___1__step__uppercase2_wic_compatible2___uppercase_message
  type: string
- id: wf4___1__step__touch_single___output
  outputSource: 1__step__touch_single/output
  type: File
requirements:
- class: SubworkflowFeatureRequirement
steps:
- id: 0__step__wf3
  in:
  - id: wf3___0__step__echo_string___message
    source: wf4___0__step__wf3___wf3___0__step__echo_string___message
  out:
  - wf3___0__step__echo_string___message_string
  - wf3___1__step__uppercase2_wic_compatible2___uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/test_workflow_builder/wf3.cwl
- id: 1__step__touch_single
  in:
  - id: touchfiles
    source: 0__step__wf3/wf3___1__step__uppercase2_wic_compatible2___uppercase_message
  out:
  - output
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/touch_single.cwl
