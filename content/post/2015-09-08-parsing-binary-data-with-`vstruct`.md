---
categories: python
comments: false
date: "2015-09-08T00:00:00Z"
title: Parsing Binary Data with `vstruct`
---

`vstruct` is a pure Python module for parsing and serializing
binary data. It is a submodule of the `vivisect` project for binary
analysis developed by 
[Invisig0th Kenshoto](http://visi.kenshoto.com/viki/MainPage).
`vstruct` been developed and tested over many years, and remains
integral a number of production systems. Its also simple and fun to learn!

`vstruct` is often a better choice than manually writing imperative
scripts using the [`struct`](https://docs.python.org/2/library/struct.html)
module. Code developed using the former
module tends to be heavily declarative, which removes the much of the
boilerplate code typically required when writing binary parsing code.
Declarative code emphasizes the imporant aspects of binary parsing:
offsets, sizes, and types. This makes maintenance of `vstruct`-based
parsers easier in the long run.

Installing `vstruct`
--------------------

[`vstruct`](https://github.com/vivisect/vivisect/tree/master/vstruct)
is a part of the [`vivisect`](https://github.com/vivisect/vivisect)
project. It is currently Python 2.7 compatible, although a
development fork exists for Python 3.x `vivisect`.

`vivisect` nor its subprojects are distributed with `setuptools`-compatible
`setup.py` files, so you should download the `vstruct` source directory
into one of your Python path directories (such as the current directory):

{{< highlight sh >}}
$ git clone https://github.com/vivisect/vivisect.git vivisect
$ cd vivisect
$ python
In [1]: import vstruct
In [2]: vstruct.isVstructType(str)
Out[2]: False
{{< / highlight >}}

Declaring a dependency on `vstruct` from a Python module via `setup.py`
is a bit tricky, so I maintain a [PyPI](https://pypi.python.org/pypi)-mirrored
package named `vivisect-vstruct-wb`. This allows you to use `pip` to install `vstruct`:

{{< highlight sh >}}
$ mkdir /tmp/env
$ virtualenv -p python2 /tmp/env
$ /tmp/env/bin/pip install vivisect-vstruct-wb
$ /tmp/env/bin/python
In [1]: import vstruct
In [2]: vstruct.isVstructType(str)
Out[2]: False
{{< / highlight >}}

I've also updated this mirror to support both Python 2.7 and Python 3.0
interpreters, so you can probably use the `vivisect-vstruct-wb` mirror
for many of your future projects. Always refer to Visi's definitive source
on GitHub before reporting bugs.

`vstruct` basics
----------------
Here's a "Hello World!" script that uses `vstruct` to parse a little endian
32-bit unsigned integer from a byte string:

{{< highlight python >}}
In [1]: import vstruct
In [2]: u32 = vstruct.primitives.v_uint32()
In [3]: u32.vsParse(b"\x01\x02\x03\x04")
In [4]: hex(u32)
Out[4]: '0x4030201'
{{< / highlight >}}

Note how you first create an instance of the `v_uint32` type, parse
a byte string using the `.vsParse()` method, and then treat the result
like a native Python type instance. To be extra safe, I like to explicitly
convert the parsed object into a true Python type:

{{< highlight python >}}
In [5]: type(u32)
Out[5]: vstruct.primitives.v_uint32

In [6]: python_u32 = int(u32)

In [7]: type(python_u32)
Out[7]: int

In [8]: hex(python_u32)
Out[8]: '0x4030201'
{{< / highlight >}}

`vstruct`-specific operations are defined as methods with the `vs` prefix.
You can find these methods on (almost) all `vstruct`-derived parsers.
Although I most commonly use `.vsParse()` and `.vsSetLength()`, its good to
be familiar with all the operations. Here's a short summary of each:

  - `.vsParse()` - parse instance from a byte string.
  - `.vsParseFd()` - parse instance from file-like object (must have `.read()` method).
  - `.vsEmit()` - serialize instance into a byte string.
  - `.vsSetValue()` - set instance's data from a native Python instance.
  - `.vsGetValue()` - get copy of instance's data as a native Python instance.
  - `.vsSetLength()` - set length of array type, such as `v_str`.
  - `.vsIsPrim()` - return `True` if instance is a simple "primitive" type.
  - `.vsGetTypeName()` - get string containing name of instance's type.
  - `.vsGetEnum()` - fetch associated `v_enum` instance for `v_number` instance, if it exists.
  - `.vsSetMeta()` - (internal)
  - `.vsCalculate()` - (internal)
  - `.vsGetMeta()` - (internal)

At this point, `vstruct` probably seems like an over-engineered clone of `struct.unpack`,
so lets dive into a cooler feature.

Complex `vstruct`s
------------------

`vstruct` parsers are typically class-based. The module provides a set
of primitive datatypes (like `v_uint32` and `v_wstr` for DWORD and
wide strings, respectively) and a mechanism for combining them into
complex datatypes (`VStruct`s). First, here are the primitive types:

  - `vstruct.primitives.v_int8` - signed integer.
  - `vstruct.primitives.v_int16`
  - `vstruct.primitives.v_int24`
  - `vstruct.primitives.v_int32`
  - `vstruct.primitives.v_int64`
  - `vstruct.primitives.v_uint8` - unsigned integer.
  - `vstruct.primitives.v_uint16`
  - `vstruct.primitives.v_uint24`
  - `vstruct.primitives.v_uint32`
  - `vstruct.primitives.v_uint64`
  - `vstruct.primitives.long`
  - `vstruct.primitives.v_float`
  - `vstruct.primitives.v_double`
  - `vstruct.primitives.v_ptr`
  - `vstruct.primitives.v_ptr32`
  - `vstruct.primitives.v_ptr64`
  - `vstruct.primitives.v_size_t`
  - `vstruct.primitives.v_bytes` - sequence of raw bytes with explicit length.
  - `vstruct.primitives.v_str` - ASCII string with explicit length.
  - `vstruct.primitives.v_wstr` - wide string with explicit length.
  - `vstruct.primitives.v_zstr` - ASCII string with NULL terminator.
  - `vstruct.primitives.v_zwstr` - wide string with NULL terminator.
  - `vstruct.primitives.GUID`
  - `vstruct.primitives.v_enum` - intepretation for integer types.
  - `vstruct.primitives.v_bitmask` - interpretation for integer types.

Complex parsers are developed by defining subclasses of the `vstruct.VStruct`
class that contain member variables that are instances of `vstruct` primitives
or other complex `VStruct` types. Whoa! Lets digest that sentence part by part.

> Complex parsers are developed by defining subclasses of the `vstruct.VStruct`
>   class...

{{< highlight python >}}
class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
{{< / highlight >}}
[source](https://github.com/vivisect/vivisect/blob/master/vstruct/defs/pe.py#L130)

In this example, we define the PE header of a Windows executable file using `vstruct`.
The name of our parser is `IMAGE_NT_HEADERS`, and it inherits from the class
`vstruct.VStruct`. We have to explicitly invoke the super constructor in our `__init__()`
method; we can use either style: 
`vstruct.VStruct.__init__(self)` or `super(IMAGE_NT_HEADERS, self).__init__()`.

> ...that contain member variables that are instances of `vstruct` primitives...

{{< highlight python >}}
class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature      = vstruct.pimitives.v_bytes(size=4)
{{< / highlight >}}
[source](https://github.com/vivisect/vivisect/blob/master/vstruct/defs/pe.py#L130)

The first member variable of a `IMAGE_NT_HEADERS` instance is a `v_bytes` instance
that holds four bytes. `v_bytes` are commonly used for raw byte sequences that don't
get parsed further. In this example, the the `.Signature` member variable will hold
the magic sequence "PE\x00\x00" when parsed from a valid PE.

Additional member variables can be added to the class definition to parse
a sequence of fields from binary data. `VStruct` classes track the order
of declaration of member variables, and handle all other associated bookkeeping.
Your only remaining job is to decide which types to use in which order. Easy!

When structure share common sub-structures, you can extract them into reusable
`VStruct` definitions that behave just like `vstruct` primitive.

> [Complex parsers are developed by defining classes that contain] other complex `VStruct` types.

{{< highlight python >}}
class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature      = v_bytes(size=4)
        self.FileHeader     = IMAGE_FILE_HEADER()
{{< / highlight >}}
[source](https://github.com/vivisect/vivisect/blob/master/vstruct/defs/pe.py#L130)

When a `VStruct` instance parses binary data and encounters a complex member variable, it recurses
into the subparser. In this example, the `.FileHeader` member variable is a complex
type defined [here](https://github.com/vivisect/vivisect/blob/master/vstruct/defs/pe.py#L80).
The `IMAGE_NT_HEADERS` parser will first consumer four bytes for the `.Signature` field,
and then pass parsing control to the `IMAGE_FILE_HEADER` complex parser. We'd need to
inspect that class's definition to determine its size and layout.

I recommend developing `VStruct` classes that each describe a small segment of a file
format, and combine them together using a master top level `VStruct`. This makes it easier
to debug, as each fragment of the parser can be independently verified. Anyways, once you've
defined a `VStruct`, you can parse data with it using the pattern described
at the beginning of the document:

{{< highlight python >}}
In [9]: 
with open("kernel32.dll", "rb") as f:
    bytez = f.read()

In [10]: hexdump.hexdump(bytez[0xf8:0x110])
Out[10]: 
00000000: 50 45 00 00 4C 01 06 00  62 67 7D 53 00 00 00 00  PE..L...bg}S....
00000010: 00 00 00 00 E0 00 0E 21                           .......!

In [11]: pe_header = IMAGE_NT_HEADERS()

In [12]: pe_header.vsParse(bytez[0xf8:0x110])

In [13]: pe_header.Signature
Out[13]: b'PE\x00\x00'

In [14]: pe_header.FileHeader.Machine
Out[14]: 332
{{< / highlight >}}

During command 9, we open a sample PE file and read its contents into a byte string.
During command 10, we show a short hexdump of the start of the PE header.
During command 11, we create an instance of the `IMAGE_NT_HEADERS` class, but note
that it doesn't yet contain any parsed data. We explicitly parse a byte string
containing the PE headers on command 12.
During commands 13 and 14, we demonstrate accessing members of the parsed instance.
*Note that when we access an embedded complex `VStruct`, we can continue to
index into it, but when we access a primitive member, we get its native Python
representation.* That's really convenient!

While debugging, we can use the `.tree()` method to print a human-readable
representation of the parsed data:

{{< highlight python >}}
In [15]: print(pe_header.tree())
Out[15]: 
00000000 (24) IMAGE_NT_HEADERS: IMAGE_NT_HEADERS
00000000 (04)   Signature: 50450000
00000004 (20)   FileHeader: IMAGE_FILE_HEADER
00000004 (02)     Machine: 0x0000014c (332)
00000006 (02)     NumberOfSections: 0x00000006 (6)
00000008 (04)     TimeDateStamp: 0x537d6762 (1400727394)
0000000c (04)     PointerToSymbolTable: 0x00000000 (0)
00000010 (04)     NumberOfSymbols: 0x00000000 (0)
00000014 (02)     SizeOfOptionalHeader: 0x000000e0 (224)
00000016 (02)     Characteristics: 0x0000210e (8462)
{{< / highlight >}}

Advanced topics in `vstruct`
----------------------------


*Conditional members*

Because a `VStruct`'s layout is declared in the type's `__init__()` constructor
method, it can react to parameters and optionally include members. For example,
a `VStruct` that behaves differently in 32- or 64-bit environments might look
something like:

{{< highlight python >}}
class FooHeader(vstruct.VStruct):
    def __init__(self, bitness=32):
        super(FooHeader, self).__init__(self)
        if bitness == 32:
            self.data_pointer = v_ptr32()
        elif bitness == 64:
            self.data_pointer = v_ptr64()
        else:
            raise RuntimeError("invalid bitness: {:d}".format(bitness))
{{< / highlight >}}

This is a very powerful technique, though its a bit tricky to get right. Its 
important to understand when they layout is finalized, and when it is evaluated
and used to parse binary data. When `__init__()` is called, the instance does
not have access to the data it will be parsing. Member variables only get populated
with parsed data once `.vsParse()` is called. *Therefore, a `VStruct` constructor
cannot refer to the contents of a member instance to decide how to continue parsing.*
For example, the following DOES NOT WORK:

{{< highlight python >}}
class BazDataRegion(vstruct.VStruct):
    def __init__(self):
        super(BazDataRegion, self).__init__()
        self.data_size = v_uint32()

        # NO! self.data_size doesn't contain anything yet!!!
        self.data_data = v_bytes(size=self.data_size)
{{< / highlight >}}


*Callbacks*

To properly handle dynamic parsers, we need to use `vstruct` callbacks.
When a `VStruct` instance finish parsing a member field, it checks to see if the
class has a specially named method prefixed with `pcb_` (*P*arser *C*all *B*ack), and
invokes it. The remainder of the method name is the name of the just-parsed field;
for example, once `BazDataRegion.data_size` is parsed, the method named `BazDataRegion.pcb_data_size`
would be invoked, if it existed.

This is important because when the callback is invoked, the `VStruct` instance is
partially populated with parsed data. For example:

{{< highlight python >}}
In [16]:
class BlipBlop(vstruct.VStruct):
    def __init__(self):
        super(BlipBlop, self).__init__()
        self.aaa = v_uint32()
        self.bbb = v_uint32()
        self.ccc = v_uint32()

    def pcb_aaa(self):
        print("pcb_aaa: aaa: %s\n" % hex(self.aaa))

    def pcb_bbb(self):
        print("pcb_bbb: aaa: %s"   % hex(self.aaa))
        print("pcb_bbb: bbb: %s\n" % hex(self.bbb))

    def pcb_ccc(self):
        print("pcb_ccc: aaa: %s"   % hex(self.aaa))
        print("pcb_ccc: bbb: %s"   % hex(self.bbb))
        print("pcb_ccc: ccc: %s\n" % hex(self.ccc))

In [17]: bb = BlipBlop()

In [18]: bb.vsParse(b"AAAABBBBCCCC")
Out[18]: 
pcb_aaa: aaa: 0x41414141

pcb_bbb: aaa: 0x41414141
pcb_bbb: bbb: 0x42424242

pcb_ccc: aaa: 0x41414141
pcb_ccc: bbb: 0x42424242
pcb_ccc: ccc: 0x43434343       
{{< / highlight >}}

This means we can defer the final initialization of a class's layout until
some binary data has been parsed. Here's the correct way of implementing a
sized buffer:

{{< highlight python >}}
In [19]:
class BazDataRegion2(vstruct.VStruct):
    def __init__(self):
        super(BazDataRegion2, self).__init__()
        self.data_size = v_uint32()
        self.data_data = v_bytes(size=0)

    def pcb_data_size(self):
        self["data_data"].vsSetLength(self.data_size)

In [20]: bdr = BazDataRegion2()

In [21]: bdr.vsParse(b"\x02\x00\x00\x00\x99\x88\x77\x66\x55\x44\x33\x22\x11")

In [22]: print(bdr.tree())
Out[22]: 
00000000 (06) BazDataRegion2: BazDataRegion2
00000000 (04)   data_size: 0x00000002 (2)
00000004 (02)   data_data: 9988
{{< / highlight >}}

During command 19, we declare a structure that has a header field (`.data_size`)
that describes the size of subsequent raw data (`.data_data`). Since we do not
have the parsed header value when `.__init__()` is called, we use a callback
named `.pcb_data_size()` that will be invoked as soon as the `.data_size` field
is parsed. When the callback executes, it updates the size of the `.data_data`
byte array so that it consumes the correct number of bytes. During command 20 we create
an instance of the parser, and on command 21 parse a byte string. Although we pass
in 13 bytes, we expect only six bytes to be consumed: four by the `.data_size` uint32,
and two for the `.data_data` byte array. The remaining bytes are not processed.
During command 22 we confirm that the parser correctly interpreted the binary data.

Note that during the `.pcb_data_size()` callback, we accessed
the `VStruct` instance object named `.data_data` by using square brackets. This is
because we want to modify that sub-instance itself, and not fetch the concrete
parsed value from that sub-instance.
It takes a little practice to figure out which technique to use
(`self.field0.xyz` or `self["field0"].xyz`), but usually if you want a concrete
parsed value, avoid square brackets. Here, we did not.


Conclusion
----------

`vstruct` is a powerful module for developing modular and maintainable binary
parsers. It removes much of the boilerplate code from the development process.
I've enjoyed using `vstruct` to parse malware C2 protocols, database indexes, and binary
XML files. I recommend you review working `vstruct` parsers from the following projects:

  - `vstruct` defs [here](https://github.com/vivisect/vivisect/tree/master/vstruct/defs)
  - `python-cim` [here](https://github.com/fireeye/flare-wmi/blob/master/python-cim/cim/cim.py) and
    [here](https://github.com/fireeye/flare-wmi/blob/master/python-cim/cim/objects.py)
  - `python-sdb` [here](https://github.com/williballenthin/python-sdb/blob/master/sdb/sdb.py)

