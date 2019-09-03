import os
from cwl_airflow import CWLJobGatherer
from biowardrobe_airflow_advanced.utils.upload import upload_deseq_results, update_genelist_table_for_deseq


class DeseqJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(DeseqJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        conf = context['dag_run'].conf
        job_result, promises = self.cwl_gather(context)
        upload_deseq_results(conf, job_result)
        update_genelist_table_for_deseq(conf, job_result)
        return job_result
