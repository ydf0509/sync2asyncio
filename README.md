# python 快速万能同步转异步语法。

```
使任意同步库快速变asyncio异步语法的方式 ，simple_run_in_executor
```

# 1 安装

pip install sync2asyncio

# 2 代码实现和测试

```python
from functools import partial
import threading
import asyncio

from threadpool_executor_shrink_able import ThreadPoolExecutorShrinkAble  # 没有使用内置的 concurrent.futures里面的，这个是优化4点功能的。

global_threadpool_executor = ThreadPoolExecutorShrinkAble(200)  # 这个是智能线程池，不是官方的concurrent.futures.threadpoolexecutor


async def simple_run_in_executor(f, *args, async_loop=None, threadpool_executor=None, **kwargs):
    """
    函数的目的是转化任何同步方法或函数为异步链路语法中的一环。例如你写一个功能，要调用10个包，其中有9个有对应的异步库，有一个还没有对应的异步库，
    因为一旦异步需要处处异步，不能因为某一个功能没有对应的异步库就前功尽弃。本函数就能够做到一个异步的链路里面调用同步库但不阻塞整个asyncio的loop循环。

    这个函数看起来很简单，主要是调用官方的 run_in_executor 。

    第1个特点是由官方的  方法改成了现在的函数 （方法是类里面面的，函数是模块下面的，我一般这么划分python方法和函数）

    第2个特点是直接内置了线程池，用户可以无需传参了。并且这个线程池功能比官方的线程池要好，可以设置一个很大的值，他会自适应自动扩大缩小。

    第3个特点是最重要的提高了易用性的地方。使用了整体偏函数把所有入参和函数生成一个偏函数，进而解决了官方只支持位置入参，不支持关键字入参的，
    当函数入参达到几十个时候，例如requests.get 如果你想设置timeout参数，如果不支持关键字入参，你需要把timeout参数之前的其他不重要参数全都传递一遍使用默认None来占位。
    函数入参个数比较多的情况下，不支持关键字入参就会很容易导致传参错误。
    不理解这个的话，你可以用原生的 run_in_executor 方法来设置requests.get函数的timeout，难度非常大。


    :param f: 任意同步阻塞函数，是非 async def的函数
    :param args:  同步函数的入参
    :param async_loop: loop
    :param threadpool_executor: 在项城市里面运行。
    :param kwargs: 同步函数的入参
    :return: 同步函数的结果
    """
    loopx = async_loop or asyncio.get_event_loop()
    # print(id(loopx))
    executor = threadpool_executor or global_threadpool_executor
    result = await loopx.run_in_executor(executor, partial(f, *args, **kwargs))
    return result


if __name__ == '__main__':
    import time
    import requests  # 这是同步阻塞函数之一


    def block_fun(x):  # 这是自定义的第二个同步阻塞函数
        time.sleep(5)
        print(x)
        return x * 10


    async def enter_fun(xx):  # 入口函数，因为为一旦异步，必须处处异步。不能直接调用block_fun，否则阻塞其他任务。
        await asyncio.sleep(1)  # # 如果你这么写  time.sleep(1)  那就完了个蛋，程序运行完成需要更长的时间。
        r = await  simple_run_in_executor(block_fun, xx)  # # 如果你这么写  r = block_fun(xx)   那就完了个蛋，程序运行完成需要更长的时间。
        print(r)
        resp = await  simple_run_in_executor(requests.get, url='http://www.baidu.com', timeout=5)
        # 如果你这么写  resp = requests.get( url='http://www.baidu.com')   那就完了个蛋，如果网站每次响应时间很大会发生严重影响，程序运行完成需要更长的时间。
        # 这个是调用了同步requests请求库，如果同步库请求一个网站需要10秒响应，asyncio中如果直接使用了同步库，会发生灭顶之灾，整个loop就成了废物。如果网站每次响应是1毫秒，那么异步中调用同步库还可以勉强接受的。
        # 但用 simple_run_in_executor来运行requests 即使网站响应时间很长，也不会对asyncio的loop产生严重阻塞影响了，这就是 simple_run_in_executor 要达到的目的。
        print(resp)


    loopy = asyncio.get_event_loop()
    print(id(loopy))
    tasks = []
    tasks.append(simple_run_in_executor(requests.get, url='http://www.baidu.com'))

    tasks.append(simple_run_in_executor(block_fun, 1))
    tasks.append(simple_run_in_executor(block_fun, 2))
    tasks.append(simple_run_in_executor(block_fun, 3))

    for i in range(100, 120):
        tasks.append(enter_fun(i))

    print('开始')
    loopy.run_until_complete(asyncio.wait(tasks))  # 通过以上可以观察到，所有的block_fun的print都是同一时间打印出来的，而不是每隔5秒一个接一个打印的。
    print('结束')


```

[![4mvIJA.png](https://z3.ax1x.com/2021/09/16/4mvIJA.png)](https://imgtu.com/i/4mvIJA)


##### 运行结果，从打印 开始到 打印结束只用了6秒

```
虽然block_fun同步函数里面需要阻塞5秒，但使用了 simple_run_in_executor 来执行这个同步阻塞函数，

虽然运行了十几个协程任务，不会造成整体整体运行时间延长。

如果不使用 simple_run_in_executor 来运行 block_fun，运行完这十几个协程任务最起码需要1分钟以上。



```

# 3 介绍作用
```
使用asyncio时候，一个调用链流程包括了5个 阻塞io的方法或函数，如果其中一个函数现在没有对应的异步库，或者新的对应异步库很难学，
快速的方式是让同步函数变成异步调用语法，可以被await，那么按上面这么封装就行了，例如假设还没有人发明aiohttp库，
世上只有requests库，你的调用链流程里面不可以直接调用requests，因为一旦这么弄，只要一个任务阻塞了，真个循环的全部任务都被阻塞了，
使用asyncio一旦异步需要处处异步，那么怎么样快速的非阻塞呢，按上面就行，使同步函数在线程池里面运行，
这个run_in_executor本质是使concurrent.futures.Future对象变成了 asyncio 里面的可等待 Future对象，所以可以被await。

 

有人会有疑问，这么不是脱了裤子放屁吗，直接在异步流程里面 使用 threadpoolexecutor.submit来运行同步阻塞函数不香吗，这不就能绕开阻塞了吗？
主要还是有个概念没搞懂，因为现在不仅是要非阻塞运行同步函数，最重要的是要在当前代码处拿到同步函数的执行结果马上使用， 
future = threadpoolexecutor.submit(block_fun,20)  然后为了得到结果需要执行future.result()，一旦使用了future.result()，
那么当前调用链又回到老问题了，那就是被阻塞。解决这个问题唯有使用  

r = await  simple_run_in_executor(block_fun, 20)，既能在线程池运行同步函数，而且为了得到结果不至于阻塞事件循环。
```

```
还有一点是为什么不使用官方的loop.run_in_executor，而是封装了一个simple_run_in_executor东西呢，
主要是因为 内置的 run_in_executor 方法，不接受关键字参数，只能接受位置参数，例如requests.get函数，入参个数高达20个，
如果严格的使用位置参数，那么requests.get函数的入参顺序必须按照定义的一样非常准确一个顺序都不能乱，必须要非常精确小心，这几乎不可能做到。

```

[![4mxQOK.png](https://z3.ax1x.com/2021/09/16/4mxQOK.png)](https://imgtu.com/i/4mxQOK)

```
 
run_in_executor必须严格的按照顺序传参，例如你想设置request的timeout值，必须在前面写很多个None来占位置；
还有例如不能把headers写在data前面，不支持关键字方式入参，很难用。使用偏函数来解决关键字入参是官方教程推荐的方式。

不理解这个的话，你可以用原生的 run_in_executor 方法来设置requests.get函数的timeout，难度非常之大，
如果是设置verify参数难上加难，越靠后的参数越难传参正确。
```
参考链接  https://docs.python.org/zh-cn/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor

```
只有使用我这个 simple_run_in_executor ，立即让同步函数化身异步语法，使同步库的函数和调用链上的其他异步库的函数能够协同作战。



run_in_executor 到底是协程程运行的还是线程运行的阻塞函数呢，毫无疑问还是线程里面运行的，在block_fun函数里面打印一下 threding.ident的线程号就可以了。
他的主要作用不是把同步变成协程运行，而是让其拥有了异步await 的用法，既能不阻塞当前事件循环，又能在同步函数执行完成return结果时拿到结果接着用。


此文分别拿blcok_fun 函数和 requests.get 函数来演示同步函数在异步调用链里面非阻塞运行，说的是快速同步变异步的方式，
归根结底还是线程运行。但是例如有人已经发明了 aiohttp 异步请求库，那就不需要使用 run_in_executor  + requests 了，最好是使用aiohttp就行了。
这个主要是为了例如 调用链路上用了10个io操作的库，其中有9个有对应的异步库，但有1个没有对应的异步库，此时不能因为现存的没有人发明这个异步库就不继续写代码罢工了吧。
```



# 4 比较asyncio.run_coroutine_threadsafe 和 run_in_executor区别

```
asyncio并发真的太难了，比线程池用法难很多，里面的概念太难了，例如介绍这两个概念。
asyncio.run_coroutine_threadsafe 和 run_in_executor 是一对反义词。

asyncio.run_coroutine_threadsafe 是在非异步的上下文环境(也就是正常的同步语法的函数里面)下调用异步函数对象（协程），
因为当前函数定义没有被async修饰，就不能在函数里面使用await，必须使用这。这个是将asyncio包的future对象转化返回一个concurrent.futures包的future对象。

run_in_executor 是在异步环境（被async修饰的异步函数）里面，调用同步函数，将函数放到线程池运行防止阻塞整个事件循环的其他任务。
这个是将 一个concurrent.futures包的future对象 转化为 asyncio包的future对象，
asyncio包的future对象是一个asyncio包的awaitable对象，所以可以被await，concurrent.futures.Future对象不能被await。
```


```