import os
import json
from cwl_airflow import CWLJobGatherer
from biowardrobe_airflow_advanced.utils.utilities import export_to_file


class PcaJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(PcaJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        conf = context['dag_run'].conf
        job_result, promises = self.cwl_gather(context)
        export_to_file(json.dumps(job_result, indent=4), os.path.join(promises["output_folder"], promises["uid"] + ".json"))
        return job_result
