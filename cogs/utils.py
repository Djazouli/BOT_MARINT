class chain_command:
    def __init__(self, name, **kwargs):
        names = name.split()
        self.last = names[-1]
        self.names = iter(names[:-1])
        self.kwargs = kwargs

    @staticmethod
    async def null():
        return

    def __call__(self, func):
        from functools import reduce
        return reduce(lambda x, y: x.group(y)(self.null), self.names, bot.group(next(self.names))(self.null)).command(self.last, **self.kwargs)(func)
