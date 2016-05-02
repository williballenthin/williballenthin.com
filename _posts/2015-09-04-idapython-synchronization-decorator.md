---
layout: post
title: "IDAPython Synchronization Decorator"
date: 2015-09-04 01:54
comments: false
categories: ida, idapython
---
One hurdle of developing multi-threaded IDAPython scripts is safely reading from
and writing to the database. IDA asks that you execute functions that may read
or write in the main thread using the `idaapi.execute_sync` function. This function
schedules the function object (the first parameter) to run at a time that is safe
to access the database.

I've often skipped this bookkeeping and hoped for the best, since it can be tedious
to marshal function object and sprinkle `idaapi.execute_sync` everwhere. To make
things painless, try using the following decorators to annotate functions that
may read from or write to the IDB:


{% highlight python %}
import functools

import idaapi


def idawrite(f):
    """
    decorator for marking a function as modifying the IDB.
    schedules a request to be made in the main IDA loop to avoid IDB corruption.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        ff = functools.partial(f, *args, **kwargs)
        return idaapi.execute_sync(ff, idaapi.MFF_WRITE)
    return wrapper


def idaread(f):
    """
    decorator for marking a function as reading from the IDB.
    schedules a request to be made in the main IDA loop to avoid
      inconsistent results.
    MFF_READ constant via: http://www.openrce.org/forums/posts/1827
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        ff = functools.partial(f, *args, **kwargs)
        return idaapi.execute_sync(ff, idaapi.MFF_READ)
    return wrapper

{% endhighlight %}

For example, here's a script that safely resets the name of the function at 0x401000:

{% highlight python %}
import idc

from idbdecorators import idawrite, idaread


@idawrite
def reset_function_name(ea):
    # reset the function name
    # via: http://stackoverflow.com/a/16774098/87207
    idc.MakeName(ea, "")
    idc.Refresh()

if __name__ == "__main__":
    reset_function_name(0x401000)
{% endhighlight %}

Enjoy!
