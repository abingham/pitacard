class Signal:
    def __init__(self):
        self._receivers = []

    def connect(self, receiver):
        self._receivers.append(receiver)

    def disconnect(self, receiver):
        for r in self._receivers:
            if r == receiver:
                self._receivers.remove(r)

    def __call__(self, *args, **kwargs):
        for r in self._receivers:
            r(*args, **kwargs)
