


async def func1():
    while True:

        print('func1() started')

        print('func1() finished')


async def func2():
    print('func2() started')
    print('func2() finished')


async def main():
    task1 = asyncio.create_task(func1())
    task2 = asyncio.create_task(func2())
    await task1
    await task2


asyncio.run(main())

# Python 3.7+
asyncio.run(main())
