from commons.systimer import SysTimer
from commons.ntptime import ntp_get_time_from_object
from commons.case_info import CaseInfo
from commons.common import Common


class ProbingResult(object):
    def __init__(self):
        super().__init__()
        self.case_info = CaseInfo()

        self.probe_id = ""
        self.matched = "Non Matched"
        self.created_date = ntp_get_time_from_object(SysTimer.now())
        self.json_result = {'time_used': 2, 'thresholds': {}, 'faces': [], 'results': []}

    def is_matched(self):
        self.matched = "Non Matched"
        if self.json_result:
            # if type(self.json_result).__name__ == "tuple":
            #     ret_error = ""
            #     for result_item in self.json_result:
            #         ret_error += str(result_item)
            #     return ret_error
            # else:
            results = self.json_result['results']
            for result in results:
                # remove % symbol from confidence
                conf_buff = result['confidence'][:len(result['confidence']) - 1]
                if float(conf_buff) >= Common.MATCH_LEVEL:
                    self.matched = "Matched"
                    break
                else:
                    self.matched = "Non Matched"
        return self.matched

    def remove_json_item(self, item):
        index = self.json_result['results'].index(item)
        if index >= 0:
            self.json_result['results'].remove(item)
            self.json_result['faces'] = self.json_result['faces'][:index] + self.json_result['faces'][index + 1:]

