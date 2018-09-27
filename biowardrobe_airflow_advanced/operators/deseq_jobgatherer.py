import os
from cwl_airflow_parser import CWLJobGatherer
from biowardrobe_airflow_advanced.utils.upload import upload_deseq
from biowardrobe_airflow_advanced.utils.analyze import get_deseq_job


class DeseqJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(DeseqJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        job_result, promises = self.cwl_gather(context)
        # conf = context['dag_run'].conf
        # job = get_deseq_job(conf)
        # upload_deseq(uid=job['uid'], filename=os.path.join(job["output_folder"], job["output_filename"]))
        return job_result