cwlVersion: v1.0
class: Workflow


requirements:
  - class: InlineJavascriptRequirement
  - class: SubworkflowFeatureRequirement


inputs:

  bam_file:
    type: File
    label: "BAM file"
    format: "http://edamontology.org/format_2572"
    doc: "BAM file"

  genelist_file:
    type: File
    label: "Genelist file"
    format: "http://edamontology.org/format_3475"
    doc: "Genelist file"

  fragment_size:
    type: int
    label: "Fragment size"
    doc: "Fragment size"

  heatmap_filename:
    type: string
    label: "Heatmap filename"
    doc: "Heatmap filename"

  threads:
    type: int?
    default: 1
    label: "Number of threads"
    doc: "Number of threads for those steps that support multithreading"


outputs:

  heatmap_file:
    type: File
    label: "TSS centered refactored homer generated heatmap JSON file"
    format: "http://edamontology.org/format_3464"
    doc: "Heatmap JSON file generated by Homer annotatePeaks.pl with TSS centered peak file"
    outputSource: convert_heatmap_to_json/heatmap_file_json


steps:

  make_tag_folders:
    in:
      bam_file: bam_file
      fragment_size: fragment_size
    out: [tag_folder]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: InlineJavascriptRequirement
      - class: InitialWorkDirRequirement
        listing: |
          ${
            return [
              {"class": "Directory",
               "basename": "default",
               "listing": [inputs.bam_file],
               "writable": true}
            ]
          }
      - class: DockerRequirement
        dockerPull: biowardrobe2/homer:v0.0.2
      inputs:
        bam_file:
          type: File
        fragment_size:
          type: int
          inputBinding:
            position: 5
            prefix: "-fragLength"
      outputs:
        tag_folder:
          type: Directory
          outputBinding:
            glob: $(inputs.bam_file.basename.split('.')[0])
      baseCommand: ["makeTagDirectory"]
      arguments:
        - valueFrom: $(inputs.bam_file.basename.split('.')[0])
        - valueFrom: $("default/" + inputs.bam_file.basename)


  center_genelist_on_tss:
    in:
      genelist_file: genelist_file
    out: [centered_genelist_file]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: DockerRequirement
        dockerPull: biowardrobe2/scidap:v0.0.3
      inputs:
        script:
          type: string?
          default: |
            cat "$0" | grep -v "refseq_id" | awk '{tss=$4; if ($6 == "-") tss=$5; print NR"\t"$3"\t"tss"\t"tss"\t"$6}' > `basename $0`
          inputBinding:
            position: 1
        genelist_file:
          type: File
          inputBinding:
            position: 2
      outputs:
        centered_genelist_file:
          type: File
          outputBinding:
            glob: "*"
      baseCommand: [bash, '-c']

  make_heatmap:
    in:
      peak_file: center_genelist_on_tss/centered_genelist_file
      tag_folder: make_tag_folders/tag_folder
      heatmap_filename: heatmap_filename
      threads: threads
    out: [heatmap_file]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: InlineJavascriptRequirement
      - class: DockerRequirement
        dockerPull: biowardrobe2/homer:v0.0.2
      inputs:
        peak_file:
          type: File
        tag_folder:
          type: Directory
          inputBinding:
            position: 8
            prefix: "-d"
        hist_width:
          type: int?
          default: 5000
          inputBinding:
            position: 9
            prefix: "-size"
        hist_bin_size:
          type: int?
          default: 200
          inputBinding:
            position: 10
            prefix: "-hist"
        threads:
          type: int?
          inputBinding:
            position: 11
            prefix: "-cpu"
        heatmap_filename:
          type: string
      outputs:
        heatmap_file:
          type: stdout
      stdout: ${return inputs.heatmap_filename;}
      baseCommand: ["annotatePeaks.pl"]
      arguments:
        - valueFrom: $(inputs.peak_file)
          position: 5
        - valueFrom: $("none")
          position: 6
        - valueFrom: $("-ghist")
          position: 7

  convert_heatmap_to_json:
    in:
      heatmap_file: make_heatmap/heatmap_file
    out: [heatmap_file_json]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: InlineJavascriptRequirement
      - class: InitialWorkDirRequirement
        listing:
          - entryname: to_json.py
            entry: |
                #!/usr/bin/env python
                import os, sys, pandas as pd
                data = pd.read_table(sys.argv[1], index_col=0)
                data.to_json(os.path.splitext(os.path.basename(sys.argv[1]))[0]+".json", orient="split")
      - class: DockerRequirement
        dockerPull: biowardrobe2/python-pandas:v0.0.1
      inputs:
        heatmap_file:
          type: File
          inputBinding:
            position: 5
      outputs:
        heatmap_file_json:
          type: File
          outputBinding:
            glob: "*.json"
      baseCommand: ["python", "to_json.py"]
