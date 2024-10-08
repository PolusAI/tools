class: CommandLineTool
cwlVersion: v1.2
inputs:
  dfPattern:
    inputBinding:
      prefix: --dfPattern
    type: string?
  ffDir:
    inputBinding:
      prefix: --ffDir
    type: Directory
  ffPattern:
    inputBinding:
      prefix: --ffPattern
    type: string
  imgDir:
    inputBinding:
      prefix: --imgDir
    type: Directory
  imgPattern:
    inputBinding:
      prefix: --imgPattern
    type: string
  outDir:
    inputBinding:
      prefix: --outDir
    type: Directory
  preview:
    inputBinding:
      prefix: --preview
    type: boolean?
outputs:
  outDir:
    outputBinding:
      glob: $(inputs.outDir.basename)
    type: Directory
requirements:
  DockerRequirement:
    dockerPull: polusai/apply-flatfield-plugin:2.0.0-dev9
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.outDir)
      writable: true
  InlineJavascriptRequirement: {}
