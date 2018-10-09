import os
from cwl_airflow_parser import CWLJobDispatcher
from biowardrobe_airflow_advanced.utils.analyze import get_deseq_job


class DeseqJobDispatcher(CWLJobDispatcher):

    def __init__(self, *args, **kwargs):
        super(DeseqJobDispatcher, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        """
            conf = {
                "condition":  [string, string],
                "groupby":     int,
                "project_uid": string,
                "name":        string,
                "uid":         string
            }
        
            "condition" is taken from $tablepairs[$i]['t1'] and $tablepairs[$i]['t2'] that are sent by client as deseq->deseq[0] and deseq->deseq[1]
            "groupby" is taken from $rtypeid that is sent by client as deseq->annottype
            "project_uid" is taken from $projectid that is sent by client project_id
            "name" is taken from $RNAME that is a updated version of deseq->name
            "uid" is taken from $UUID and is randomly generated      
                    
            "groupby": 1 - group by isoforms
                       2 - group by genes
                       3 - group by common tss
            
            This is what we get from the client
                {
                  "project_id": string,
                  "atype_id": int,
                  "deseq": {
                    "name": string,
                    "annottype": int,
                    "seriestype": int,
                    "deseq": [{
                      "order": int,
                      "table": string
                    }, {
                      "order": int,
                      "table": string
                    }]
                  }
                }
        """
        conf = context['dag_run'].conf
        try:
            return self.cwl_dispatch(conf['job'])
        except KeyError:
            return self.cwl_dispatch(get_deseq_job(conf))

