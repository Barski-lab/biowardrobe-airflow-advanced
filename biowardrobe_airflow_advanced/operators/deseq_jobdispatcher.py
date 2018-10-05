import os
from cwl_airflow_parser import CWLJobDispatcher
from biowardrobe_airflow_advanced.utils.analyze import get_deseq_job


class DeseqJobDispatcher(CWLJobDispatcher):

    def __init__(self, *args, **kwargs):
        super(DeseqJobDispatcher, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        """
        conf = {"condition":["untreated_uid", "treated_uid"], "groupby":1, "result_uid":"uid"}
            "groupby": 1 - group by isoforms
            "groupby": 2 - group by genes
            "groupby": 3 - group by common tss
        """
        conf = context['dag_run'].conf
        try:
            return self.cwl_dispatch(conf['job'])
        except KeyError:
            return self.cwl_dispatch(get_deseq_job(conf))

