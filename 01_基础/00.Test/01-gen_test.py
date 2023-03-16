
def myGen():
    print('生成器被调用')
    yield 1
    yield 2
    yield 3
    return 4


def myFun():
    return 4



"""
    1.调用myGen() 函数,则会返回iterable对象
    2.开始迭代循环,执行到yield 1 则会停止,下次循环会从yield 2 开始执行然后停止,下次循环yield3开始执行最终迭代停止
    
"""

print(myFun())
print(myGen())

mygen = myGen()
print(next(mygen))
print(next(mygen))
print(next(mygen))
