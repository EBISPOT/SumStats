
class AlreadyLoadedError(Exception):
    def __init__(self, already_loaded):
        super().__init__("%s already loaded!" %(already_loaded))


class NotFoundError(Exception):
    def __init__(self, item_not_found):
        super().__init__("%s does not exist!" %(item_not_found))
