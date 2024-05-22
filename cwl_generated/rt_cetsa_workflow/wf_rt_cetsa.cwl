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
- id: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___filePattern
  type: string?
- id: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___mask
  type: string?
- id: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___outDir
  type: Directory
- id: wf_rt_cetsa___2__step__rt_cetsa_moltenprot___filePattern
  type: string?
- id: wf_rt_cetsa___2__step__rt_cetsa_moltenprot___outDir
  type: Directory
- id: wf_rt_cetsa___3__step__rt_cetsa_analysis___outDir
  type: Directory
- id: wf_rt_cetsa___3__step__rt_cetsa_analysis___params
  type: string
- id: wf_rt_cetsa___3__step__rt_cetsa_analysis___platemap
  type: File
- id: wf_rt_cetsa___3__step__rt_cetsa_analysis___values
  type: string
outputs:
- id: wf_rt_cetsa___0__step__rt_cetsa_plate_extraction___outDir
  outputSource: 0__step__rt_cetsa_plate_extraction/outDir
  type: Directory
- id: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___outDir
  outputSource: 1__step__rt_cetsa_intensity_extraction/outDir
  type: Directory
- id: wf_rt_cetsa___2__step__rt_cetsa_moltenprot___outDir
  outputSource: 2__step__rt_cetsa_moltenprot/outDir
  type: Directory
- id: wf_rt_cetsa___3__step__rt_cetsa_analysis___outDir
  outputSource: 3__step__rt_cetsa_analysis/outDir
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
- id: 1__step__rt_cetsa_intensity_extraction
  in:
  - id: filePattern
    source: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___filePattern
  - id: inpDir
    source: 0__step__rt_cetsa_plate_extraction/outDir
  - id: mask
    source: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___mask
  - id: outDir
    source: wf_rt_cetsa___1__step__rt_cetsa_intensity_extraction___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-plugins/features/rt-cetsa-intensity-extraction-tool/rt_cetsa_intensity_extraction.cwl
- id: 2__step__rt_cetsa_moltenprot
  in:
  - id: filePattern
    source: wf_rt_cetsa___2__step__rt_cetsa_moltenprot___filePattern
  - id: inpDir
    source: 1__step__rt_cetsa_intensity_extraction/outDir
  - id: outDir
    source: wf_rt_cetsa___2__step__rt_cetsa_moltenprot___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/tabular-tools/regression/rt-cetsa-moltenprot-tool/rt_cetsa_moltenprot.cwl
- id: 3__step__rt_cetsa_analysis
  in:
  - id: inpDir
    source: 2__step__rt_cetsa_moltenprot/outDir
  - id: outDir
    source: wf_rt_cetsa___3__step__rt_cetsa_analysis___outDir
  - id: params
    source: wf_rt_cetsa___3__step__rt_cetsa_analysis___params
  - id: platemap
    source: wf_rt_cetsa___3__step__rt_cetsa_analysis___platemap
  - id: values
    source: wf_rt_cetsa___3__step__rt_cetsa_analysis___values
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/tabular-tools/regression/rt-cetsa-analysis-tool/rt_cetsa_analysis.cwl
