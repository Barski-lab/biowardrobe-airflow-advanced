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

  json_filename:
    type: string
    label: "Output JSON filename"
    doc: "Output JSON filename"

  plot_name:
    type: string
    label: "Display name for plot"
    doc: "Display name for plot"

  threads:
    type: int
    default: 1
    label: "Number of threads"
    doc: "Number of threads for those steps that support multithreading"


outputs:

  json_file:
    type: File
    label: "Heatmap & Genebody Histogram"
    format: "http://edamontology.org/format_3464"
    doc: "TSS centered heatmap and genebody histogram combined JSON file"
    outputSource: convert_to_json/json_file


steps:

  make_tag_folder:
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

  make_tss_centered_peak_file:
    in:
      genelist_file: genelist_file
    out: [tss_centered_peak_file]
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
        tss_centered_peak_file:
          type: File
          outputBinding:
            glob: "*"
      baseCommand: [bash, '-c']

  make_peak_file:
    in:
      genelist_file: genelist_file
    out: [peak_file]
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
            cat "$0" | grep -v "refseq_id" | awk '{print NR"\t"$3"\t"$4"\t"$5"\t"$6}' > `basename $0`
          inputBinding:
            position: 1
        genelist_file:
          type: File
          inputBinding:
            position: 2
      outputs:
        peak_file:
          type: File
          outputBinding:
            glob: "*"
      baseCommand: [bash, '-c']

  make_genebody_hist:
    in:
      peak_file: make_peak_file/peak_file
      tag_folders: make_tag_folder/tag_folder
      flank_width:
        default: 5000
      flank_bin_size:
        default: 5
      genebody_bin_count:
        default: 1000
      norm_fpkm:
        default: True
      norm_fragment_size: fragment_size
      genebody_to_flank_ratio:
        default: 1
      genebody_hist_filename: json_filename
      threads: threads
    out: [genebody_hist_file]
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
        tag_folders:
          type: Directory
          inputBinding:
            position: 7
            prefix: "-d"
        flank_width:
          type: int
          inputBinding:
            position: 8
            prefix: "-size"
        flank_bin_size:
          type: int
          inputBinding:
            position: 9
            prefix: "-bin"
        genebody_bin_count:
          type: int
          inputBinding:
            position: 10
            prefix: "-gbin"
        norm_fpkm:
          type: boolean
          inputBinding:
            position: 11
            prefix: "-fpkm"
        norm_fragment_size:
          type: int
          inputBinding:
            position: 17
            prefix: "-normLength"
        genebody_to_flank_ratio:
          type: int
          inputBinding:
            position: 18
            prefix: "-gRatio"
        threads:
          type: int?
          inputBinding:
            position: 19
            prefix: "-cpu"
        genebody_hist_filename:
          type: string
      outputs:
        genebody_hist_file:
          type: stdout
      stdout: ${return inputs.genebody_hist_filename;}
      baseCommand: ["makeMetaGeneProfile.pl"]
      arguments:
        - valueFrom: $(inputs.peak_file)
          position: 5
        - valueFrom: $("none")
          position: 6

  make_heatmap:
    in:
      peak_file: make_tss_centered_peak_file/tss_centered_peak_file
      tag_folder: make_tag_folder/tag_folder
      heatmap_filename: json_filename
      hist_width:
        default: 10000
      hist_bin_size:
        default: 400
      norm_fpkm:
        default: True
      norm_fragment_size: fragment_size
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
          type: int
          inputBinding:
            position: 9
            prefix: "-size"
        hist_bin_size:
          type: int
          inputBinding:
            position: 10
            prefix: "-hist"
        threads:
          type: int
          inputBinding:
            position: 11
            prefix: "-cpu"
        norm_fpkm:
          type: boolean
          inputBinding:
            position: 12
            prefix: "-fpkm"
        norm_fragment_size:
          type: int
          inputBinding:
            position: 13
            prefix: "-normLength"
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

  make_atdp_hist:
    in:
      peak_file: make_tss_centered_peak_file/tss_centered_peak_file
      tag_folder: make_tag_folder/tag_folder
      atdp_hist_filename: json_filename
      hist_width:
        default: 10000
      hist_bin_size:
        default: 5
      norm_fpkm:
        default: True
      norm_fragment_size: fragment_size
      threads: threads
    out: [atdp_hist_file]
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
          type: int
          inputBinding:
            position: 9
            prefix: "-size"
        hist_bin_size:
          type: int
          inputBinding:
            position: 10
            prefix: "-hist"
        threads:
          type: int
          inputBinding:
            position: 11
            prefix: "-cpu"
        norm_fpkm:
          type: boolean
          inputBinding:
            position: 12
            prefix: "-fpkm"
        norm_fragment_size:
          type: int
          inputBinding:
            position: 13
            prefix: "-normLength"
        atdp_hist_filename:
          type: string
      outputs:
        atdp_hist_file:
          type: stdout
      stdout: ${return inputs.atdp_hist_filename;}
      baseCommand: ["annotatePeaks.pl"]
      arguments:
        - valueFrom: $(inputs.peak_file)
          position: 5
        - valueFrom: $("none")
          position: 6

  convert_to_json:
    in:
      heatmap_file: make_heatmap/heatmap_file
      genebody_hist_file: make_genebody_hist/genebody_hist_file
      atdp_hist_file: make_atdp_hist/atdp_hist_file
      genebody_smooth_window:
        default: 20
      atdp_smooth_window:
        default: 10
      plot_name: plot_name
    out: [json_file]
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
              import os, sys, pandas as pd, numpy as np
              from json import dumps
              hm_df = pd.read_table(sys.argv[1], index_col=0)
              gb_df = pd.read_table(sys.argv[2], index_col=0, header=0, names=["coverage", "pos_tags", "neg_tags"])
              td_df = pd.read_table(sys.argv[3], index_col=0, header=0, names=["coverage", "pos_tags", "neg_tags"])
              def smooth(y, b):
                  s = np.r_[y[b - 1:0:-1], y, y[-2:-b - 1:-1]]
                  w = np.ones(b, 'd')
                  y = np.convolve(w / w.sum(), s, mode='same')
                  return y[b - 1:-(b - 1)]
              gb_df['smooth'] = pd.Series(smooth(gb_df['pos_tags'] + gb_df['neg_tags'], int(sys.argv[4])), index=gb_df.index)
              td_df['smooth'] = pd.Series(smooth(td_df['pos_tags'] + td_df['neg_tags'], int(sys.argv[5])), index=td_df.index)
              d = {
                  "heatmap":   hm_df.to_dict(orient="split"),
                  "genebody":  gb_df.to_dict(orient="split"),
                  "atdp":      td_df.to_dict(orient="split")
                  "plot_name": sys.argv[6]
              }
              with open(os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".json", 'w') as s:
                  s.write(dumps(d))
      - class: DockerRequirement
        dockerPull: biowardrobe2/python-pandas:v0.0.1
      inputs:
        heatmap_file:
          type: File
          inputBinding:
            position: 5
        genebody_hist_file:
          type: File
          inputBinding:
            position: 6
        atdp_hist_file:
          type: File
          inputBinding:
            position: 7
        genebody_smooth_window:
          type: int
          inputBinding:
            position: 8
        atdp_smooth_window:
          type: int
          inputBinding:
            position: 9
        plot_name:
          type: string
          inputBinding:
            position: 10
      outputs:
        json_file:
          type: File
          outputBinding:
            glob: "*.json"
      baseCommand: ["python", "to_json.py"]
