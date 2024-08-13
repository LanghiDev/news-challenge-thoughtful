from RPA.Robocorp.WorkItems import WorkItems
'''
Get parameters via the robocloud work item
'''

class Config:
    def __init__(self):
        work_item = WorkItems()
        work_item.get_input_work_item()
        self.variables = work_item.get_work_item_variables()

    def get_search_phrase(self):
        return self.variables["SEARCH_PHRASE"]
        
    def get_months(self):
        return self.variables["MONTHS"]

"""
{
  "SEARCH_PHRASE": "Sleeping",
  "MONTHS": 1
}
"""