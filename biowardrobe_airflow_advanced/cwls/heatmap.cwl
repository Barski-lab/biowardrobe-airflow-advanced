cwlVersion: v1.0
class: Workflow


requirements:
  - class: InlineJavascriptRequirement
  - class: SubworkflowFeatureRequirement


inputs:

  bam_file:
    type: File[]
    label: "BAM files"
    format: "http://edamontology.org/format_2572"
    doc: "Array of input BAM files"

  genelist_file:
    type: File
    label: "Genelist file"
    format: "http://edamontology.org/format_3475"
    doc: "Genelist file"

  fragment_size:
    type: int[]
    label: "Fragment sizes"
    doc: "Array of fragment sizes"

  threads:
    type: int?
    default: 1
    label: "Number of threads"
    doc: "Number of threads for those steps that support multithreading"


outputs:

  heatmap_file:
    type: File[]
    label: "TSS centered refactored homer generated heatmap JSON files"
    format: "http://edamontology.org/format_3464"
    doc: "Heatmap JSON files generated by Homer annotatePeaks.pl with TSS centered peak file"
    outputSource: split_heatmap/refactored_heatmap_file


steps:

  make_tag_folders:
    in:
      bam_file: bam_file
      fragment_size: fragment_size
    out: [tag_folder]
    run:
      cwlVersion: v1.0
      class: Workflow
      requirements:
        - class: ScatterFeatureRequirement
        - class: StepInputExpressionRequirement
        - class: InlineJavascriptRequirement
      inputs:
        bam_file:
          type: File[]
        fragment_size:
          type: int[]
      outputs:
        tag_folder:
          type: Directory[]
          outputSource: make_tag_directory/output_tag_folder
      steps:
        make_tag_directory:
          in:
            bam_file: bam_file
            fragment_size: fragment_size
          scatter:
            - bam_file
            - fragment_size
          scatterMethod: dotproduct
          out: [output_tag_folder]
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
              dockerPull: biowardrobe2/homer:v0.0.1
            inputs:
              bam_file:
                type: File
              fragment_size:
                type: int
                inputBinding:
                  position: 5
                  prefix: "-fragLength"
            outputs:
              output_tag_folder:
                type: Directory
                outputBinding:
                  glob: $(inputs.bam_file.basename.split('.')[0])
            baseCommand: ["makeTagDirectory"]
            arguments:
              - valueFrom: $(inputs.bam_file.basename.split('.')[0])
              - valueFrom: $("default/" + inputs.bam_file.basename)

  center_genelist_on_tss:
    in:
      input_file: genelist_file
    out: [output_file]
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
        input_file:
          type: File
          inputBinding:
            position: 2
      outputs:
        output_file:
          type: File
          outputBinding:
            glob: "*"
      baseCommand: [bash, '-c']

  make_tss_heatmap:
    in:
      peak_file: center_genelist_on_tss/output_file
      tag_folders: make_tag_folders/tag_folder
      export_heatmap:
        default: True
      threads: threads
    out: [histogram_file]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: InlineJavascriptRequirement
      - class: DockerRequirement
        dockerPull: biowardrobe2/homer:v0.0.1
      inputs:
        peak_file:
          type: File
        tag_folders:
          type: Directory[]
          inputBinding:
            position: 7
            prefix: "-d"
        hist_width:
          type: int?
          default: 5000
          inputBinding:
            position: 8
            prefix: "-size"
        hist_bin_size:
          type: int?
          default: 200
          inputBinding:
            position: 9
            prefix: "-hist"
        export_heatmap:
          type: boolean?
          inputBinding:
            position: 10
            prefix: "-ghist"
        threads:
          type: int?
          inputBinding:
            position: 16
            prefix: "-cpu"
        histogram_filename:
          type: string
          default: "default.tsv"
      outputs:
        histogram_file:
          type: stdout
      stdout: ${return inputs.histogram_filename;}
      baseCommand: ["annotatePeaks.pl"]
      arguments:
        - valueFrom: $(inputs.peak_file)
          position: 5
        - valueFrom: $("none")
          position: 6

  split_heatmap:
    in:
      heatmap_file: make_tss_heatmap/histogram_file
      output_filename: bam_file
    out: [refactored_heatmap_file]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: InlineJavascriptRequirement
      - class: InitialWorkDirRequirement
        listing:
          - entryname: split.py
            entry: |
                #!/usr/bin/env python
                import os
                import sys
                import pandas as pd
                heatmap_file = sys.argv[1]
                output_files = [os.path.splitext(os.path.basename(file))[0]+".json" for file in sys.argv[2:]]
                print (output_files)
                data = pd.read_table(heatmap_file, index_col=0)
                size = int(len(data.columns)/len(output_files))
                data = [data[c] for c in [data.columns[i*size:(i+1)*size] for i in range(len(output_files))]]
                for idx,d in enumerate(data):
                    d.columns = data[0].columns
                    d.to_json(output_files[idx], orient="split")
      - class: DockerRequirement
        dockerPull: biowardrobe2/python-pandas:v0.0.1
      inputs:
        heatmap_file:
          type: File
          inputBinding:
            position: 5
        output_filename:
          type: File[]
          inputBinding:
            position: 6
      outputs:
        refactored_heatmap_file:
          type: File[]
          outputBinding:
            glob: "*.json"
      baseCommand: ["python", "split.py"]
