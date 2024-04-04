class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/debug_image_processing_2/wf_image_processing.cwl
inputs:
- id: wf_image_processing___0__step__bbbcdownload___name
  type: string
- id: wf_image_processing___0__step__bbbcdownload___outDir
  type: Directory
- id: wf_image_processing___1__step__file-renaming___filePattern
  type: string
- id: wf_image_processing___1__step__file-renaming___mapDirectory
  type: string?
- id: wf_image_processing___1__step__file-renaming___outDir
  type: Directory
- id: wf_image_processing___1__step__file-renaming___outFilePattern
  type: string
- id: wf_image_processing___1__step__file-renaming___preview
  type: boolean?
- id: wf_image_processing___2__step__ome-converter___fileExtension
  type: string
- id: wf_image_processing___2__step__ome-converter___filePattern
  type: string
- id: wf_image_processing___2__step__ome-converter___outDir
  type: Directory
- id: wf_image_processing___3__step__montage___filePattern
  type: string
- id: wf_image_processing___3__step__montage___layout
  type: string?
- id: wf_image_processing___3__step__montage___outDir
  type: Directory
- id: wf_image_processing___4__step__image_assembler___outDir
  type: Directory
- id: wf_image_processing___5__step__precompute_slide___filePattern
  type: string?
- id: wf_image_processing___5__step__precompute_slide___imageType
  type: string
- id: wf_image_processing___5__step__precompute_slide___outDir
  type: Directory
- id: wf_image_processing___5__step__precompute_slide___pyramidType
  type: string
outputs:
- id: wf_image_processing___0__step__bbbcdownload___outDir
  outputSource: 0__step__bbbcdownload/outDir
  type: Directory
- id: wf_image_processing___1__step__file-renaming___outDir
  outputSource: 1__step__file-renaming/outDir
  type: Directory
- id: wf_image_processing___1__step__file-renaming___preview_json
  outputSource: 1__step__file-renaming/preview_json
  type: File
- id: wf_image_processing___2__step__ome-converter___outDir
  outputSource: 2__step__ome-converter/outDir
  type: Directory
- id: wf_image_processing___3__step__montage___global_positions
  outputSource: 3__step__montage/global_positions
  type: File
- id: wf_image_processing___3__step__montage___outDir
  outputSource: 3__step__montage/outDir
  type: Directory
- id: wf_image_processing___3__step__montage___preview_json
  outputSource: 3__step__montage/preview_json
  type: File
- id: wf_image_processing___4__step__image_assembler___assembled_image
  outputSource: 4__step__image_assembler/assembled_image
  type: File
- id: wf_image_processing___4__step__image_assembler___outDir
  outputSource: 4__step__image_assembler/outDir
  type: Directory
- id: wf_image_processing___4__step__image_assembler___preview_json
  outputSource: 4__step__image_assembler/preview_json
  type: File
- id: wf_image_processing___5__step__precompute_slide___outDir
  outputSource: 5__step__precompute_slide/outDir
  type: Directory
requirements: []
steps:
- id: 0__step__bbbcdownload
  in:
  - id: name
    source: wf_image_processing___0__step__bbbcdownload___name
  - id: outDir
    source: wf_image_processing___0__step__bbbcdownload___outDir
  out:
  - outDir
  run: https://raw.githubusercontent.com/PolusAI/image-workflows/main/cwl_adapters/bbbcdownload.cwl
- id: 1__step__file-renaming
  in:
  - id: filePattern
    source: wf_image_processing___1__step__file-renaming___filePattern
  - id: inpDir
    source: 0__step__bbbcdownload/outDir
  - id: mapDirectory
    source: wf_image_processing___1__step__file-renaming___mapDirectory
  - id: outDir
    source: wf_image_processing___1__step__file-renaming___outDir
  - id: outFilePattern
    source: wf_image_processing___1__step__file-renaming___outFilePattern
  - id: preview
    source: wf_image_processing___1__step__file-renaming___preview
  out:
  - outDir
  - preview_json
  run: https://raw.githubusercontent.com/PolusAI/image-workflows/main/cwl_adapters/file-renaming.cwl
- id: 2__step__ome-converter
  in:
  - id: fileExtension
    source: wf_image_processing___2__step__ome-converter___fileExtension
  - id: filePattern
    source: wf_image_processing___2__step__ome-converter___filePattern
  - id: inpDir
    source: 1__step__file-renaming/outDir
  - id: outDir
    source: wf_image_processing___2__step__ome-converter___outDir
  out:
  - outDir
  run: https://raw.githubusercontent.com/PolusAI/image-workflows/main/cwl_adapters/ome-converter.cwl
- id: 3__step__montage
  in:
  - id: filePattern
    source: wf_image_processing___3__step__montage___filePattern
  - id: inpDir
    source: 2__step__ome-converter/outDir
  - id: layout
    source: wf_image_processing___3__step__montage___layout
  - id: outDir
    source: wf_image_processing___3__step__montage___outDir
  out:
  - global_positions
  - outDir
  - preview_json
  run: https://raw.githubusercontent.com/PolusAI/image-workflows/main/cwl_adapters/montage.cwl
- id: 4__step__image_assembler
  in:
  - id: imgPath
    source: 2__step__ome-converter/outDir
  - id: outDir
    source: wf_image_processing___4__step__image_assembler___outDir
  - id: stitchPath
    source: 3__step__montage/outDir
  out:
  - assembled_image
  - outDir
  - preview_json
  run: https://raw.githubusercontent.com/PolusAI/image-workflows/main/cwl_adapters/image_assembler.cwl
- id: 5__step__precompute_slide
  in:
  - id: filePattern
    source: wf_image_processing___5__step__precompute_slide___filePattern
  - id: imageType
    source: wf_image_processing___5__step__precompute_slide___imageType
  - id: inpDir
    source: 4__step__image_assembler/outDir
  - id: outDir
    source: wf_image_processing___5__step__precompute_slide___outDir
  - id: pyramidType
    source: wf_image_processing___5__step__precompute_slide___pyramidType
  out:
  - outDir
  run: https://raw.githubusercontent.com/PolusAI/image-workflows/main/cwl_adapters/precompute_slide.cwl
