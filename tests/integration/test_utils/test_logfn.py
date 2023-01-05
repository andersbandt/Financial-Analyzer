from utils import logfn

@logfn
def test(a, b):
    import time
    time.sleep(1)
    return a + b

print(test(1, 2))

