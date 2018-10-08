import os
from cwl_airflow_parser import CWLJobDispatcher
from biowardrobe_airflow_advanced.utils.analyze import get_deseq_job


class DeseqJobDispatcher(CWLJobDispatcher):

    def __init__(self, *args, **kwargs):
        super(DeseqJobDispatcher, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        """
            conf = {
                "condition": ["untreated_uid", "treated_uid"],
                "groupby": 1,
                "project_uid": "project_id",
                "name": "name",
                "uid": "uid"
            }
        
            "condition" is taken from $tablepairs[$i]['t1'] and $tablepairs[$i]['t2'] that are sent by client as deseq->deseq[0] and deseq->deseq[1]
            "groupby" is taken from $rtypeid that is sent by client as deseq->annottype
            "project_uid" is taken from $projectid that is sent by client project_id
            "name" is taken from $RNAME that is a updated version of deseq->name
            "uid" is taken from $UUID and is randomly generated      
                    
            "groupby": 1 - group by isoforms
            "groupby": 2 - group by genes
            "groupby": 3 - group by common tss
            
            This is an example of what we get from the client
                {
                  "project_id": "y7effa94-941a-4428-c79d-7a155c86e3bd",
                  "atype_id": 3,
                  "deseq": {
                    "name": "test_run",
                    "annottype": 1,
                    "seriestype": 1,
                    "deseq": [{
                      "order": 1,
                      "table": "B751bbab-128e-4354-ee21-0274d007ff13"
                    }, {
                      "order": 2,
                      "table": "d2617dbc-6fdb-4f97-8bdf-93de2a2420c1"
                    }]
                  }
                }
            
        """
        conf = context['dag_run'].conf
        try:
            return self.cwl_dispatch(conf['job'])
        except KeyError:
            return self.cwl_dispatch(get_deseq_job(conf))

