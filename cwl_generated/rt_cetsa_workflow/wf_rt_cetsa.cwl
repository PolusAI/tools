class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/rt_cetsa_workflow/wf_rt_cetsa.cwl
inputs:
- id: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___filePattern
  type: string?
- id: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___inpDir
  type: Directory
- id: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___outDir
  type: Directory
outputs:
- id: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___outDir
  outputSource: 0__step__rt_cetsa_plate_extraction/outDir
  type: Directory
requirements: []
steps:
- id: 0__step__rt_cetsa_plate_extraction
  in:
  - id: filePattern
    source: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___filePattern
  - id: inpDir
    source: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___inpDir
  - id: outDir
    source: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-plugins/segmentation/rt-cetsa-plate-extraction-tool/rt_cetsa_plate_extraction.cwl
