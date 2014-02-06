from . import util

class QueryError(Exception):
    def __init__(self, data, *args):
        self.data = data
        msg = data['resultSet']['errorMessage']['content']
        self.query_time = util.parse_trimet_time(data['resultSet']['queryTime'])
        super().__init__(msg, *args)
