import os
from cwl_airflow_parser import CWLJobGatherer
from biowardrobe_airflow_advanced.utils.upload import upload_deseq


class DeseqJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(DeseqJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        job_result, promises = self.cwl_gather(context)
        # upload_deseq(uid=promises['uid'], filename=os.path.join(promises["output_folder"], promises["output_filename"]))
        return job_result