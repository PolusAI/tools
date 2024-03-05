class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/demo_image_processing/wf_image_processing.cwl
inputs:
- id: wf_image_processing___0__step__BbbcDownload___name
  type: string
- id: wf_image_processing___0__step__BbbcDownload___outDir
  type: Directory
- id: wf_image_processing___1__step__FileRenaming___filePattern
  type: string
- id: wf_image_processing___1__step__FileRenaming___mapDirectory
  type: string?
- id: wf_image_processing___1__step__FileRenaming___outDir
  type: Directory
- id: wf_image_processing___1__step__FileRenaming___outFilePattern
  type: string
- id: wf_image_processing___2__step__OmeConverter___fileExtension
  type: string
- id: wf_image_processing___2__step__OmeConverter___filePattern
  type: string
- id: wf_image_processing___2__step__OmeConverter___outDir
  type: Directory
- id: wf_image_processing___3__step__Montage___filePattern
  type: string
- id: wf_image_processing___3__step__Montage___layout
  type: string?
- id: wf_image_processing___3__step__Montage___outDir
  type: Directory
- id: wf_image_processing___4__step__ImageAssembler___outDir
  type: Directory
- id: wf_image_processing___5__step__PrecomputeSlide___filePattern
  type: string?
- id: wf_image_processing___5__step__PrecomputeSlide___imageType
  type: string?
- id: wf_image_processing___5__step__PrecomputeSlide___outDir
  type: Directory
- id: wf_image_processing___5__step__PrecomputeSlide___pyramidType
  type: string
outputs:
- id: wf_image_processing___0__step__BbbcDownload___outDir
  outputSource: 0__step__BbbcDownload/outDir
  type: Directory
- id: wf_image_processing___1__step__FileRenaming___outDir
  outputSource: 1__step__FileRenaming/outDir
  type: Directory
- id: wf_image_processing___2__step__OmeConverter___outDir
  outputSource: 2__step__OmeConverter/outDir
  type: Directory
- id: wf_image_processing___3__step__Montage___outDir
  outputSource: 3__step__Montage/outDir
  type: Directory
- id: wf_image_processing___4__step__ImageAssembler___outDir
  outputSource: 4__step__ImageAssembler/outDir
  type: Directory
- id: wf_image_processing___5__step__PrecomputeSlide___outDir
  outputSource: 5__step__PrecomputeSlide/outDir
  type: Directory
requirements: []
steps:
- id: 0__step__BbbcDownload
  in:
  - id: name
    source: wf_image_processing___0__step__BbbcDownload___name
  - id: outDir
    source: wf_image_processing___0__step__BbbcDownload___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl/image_tools/BbbcDownload.cwl
- id: 1__step__FileRenaming
  in:
  - id: filePattern
    source: wf_image_processing___1__step__FileRenaming___filePattern
  - id: inpDir
    source: 0__step__BbbcDownload/outDir
  - id: mapDirectory
    source: wf_image_processing___1__step__FileRenaming___mapDirectory
  - id: outDir
    source: wf_image_processing___1__step__FileRenaming___outDir
  - id: outFilePattern
    source: wf_image_processing___1__step__FileRenaming___outFilePattern
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl/image_tools/FileRenaming.cwl
- id: 2__step__OmeConverter
  in:
  - id: fileExtension
    source: wf_image_processing___2__step__OmeConverter___fileExtension
  - id: filePattern
    source: wf_image_processing___2__step__OmeConverter___filePattern
  - id: inpDir
    source: 1__step__FileRenaming/outDir
  - id: outDir
    source: wf_image_processing___2__step__OmeConverter___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl/image_tools/OmeConverter.cwl
- id: 3__step__Montage
  in:
  - id: filePattern
    source: wf_image_processing___3__step__Montage___filePattern
  - id: inpDir
    source: 2__step__OmeConverter/outDir
  - id: layout
    source: wf_image_processing___3__step__Montage___layout
  - id: outDir
    source: wf_image_processing___3__step__Montage___outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl/image_tools/Montage.cwl
- id: 4__step__ImageAssembler
  in:
  - id: imgPath
    source: 2__step__OmeConverter/outDir
  - id: outDir
    source: wf_image_processing___4__step__ImageAssembler___outDir
  - id: stitchPath
    source: 3__step__Montage/outDir
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl/image_tools/ImageAssembler.cwl
- id: 5__step__PrecomputeSlide
  in:
  - id: filePattern
    source: wf_image_processing___5__step__PrecomputeSlide___filePattern
  - id: imageType
    source: wf_image_processing___5__step__PrecomputeSlide___imageType
  - id: inpDir
    source: 4__step__ImageAssembler/outDir
  - id: outDir
    source: wf_image_processing___5__step__PrecomputeSlide___outDir
  - id: pyramidType
    source: wf_image_processing___5__step__PrecomputeSlide___pyramidType
  out:
  - outDir
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl/image_tools/PrecomputeSlide.cwl
