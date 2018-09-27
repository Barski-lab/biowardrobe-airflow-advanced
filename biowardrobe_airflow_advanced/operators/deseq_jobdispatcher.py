import os
from cwl_airflow_parser import CWLJobDispatcher
from biowardrobe_airflow_advanced.utils.analyze import get_deseq_job


class DeseqJobDispatcher(CWLJobDispatcher):

    def __init__(self, *args, **kwargs):
        super(DeseqJobDispatcher, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        # conf = {"condition":["untreated_uid", "treated_uid"], "groupby":"isoform", "result_uid":"uid"}
        conf = context['dag_run'].conf
        try:
            return self.cwl_dispatch(conf['job'])
        except KeyError:
            return self.cwl_dispatch(get_deseq_job(conf))

