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

    第3个特点是最重要的提高了易用性的地方。使用了整体偏函数，进而解决了官方只支持位置入参，不支持关键字入参的，
    当函数入参达到几十个时候，例如requests.get 如果你想设置timeout参数，如果不支持关键字入参，你需要把timeout参数之前的其他不重要参数全都传递一遍使用默认None来占位。
    函数入参个数比较多的情况下，不支持关键字入参就会很容易导致传参错误。


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
        resp = await  simple_run_in_executor(requests.get, url='http://www.baidu.com')
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
