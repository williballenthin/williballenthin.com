---
title: "Sketch: Modern Python in Ghidra"
date: 2020-05-20T00:00:00-07:00
draft: false
---

This is a set of notes as I brainstorm.


## the problem: Ghidra only supports Jython 2.7

[We](http://flare-on.com/) have been developing a [binary analysis tool](https://twitter.com/williballenthin/status/1262853393829130240).
More details on that at a later date.

It runs upon existing disassembler frameworks, including vivisect (Python 2.7), IDA Pro (non-free), and potentially miasm (Python 3).
I think it would be cool to also support [Ghidra](https://ghidra-sre.org/) because its free, powerful, and has a great community.

*But*, Ghidra only supports Jython - a Python 2.7 interpreter implemented in Java that has no planned support for Python 3.
Unfortunately, there are [further restrictions](https://github.com/yaml/pyyaml/issues/369) around Jython, too.

What I'd really like is to develop scripts in modern Python (e.g. 3.8) for Ghidra.
This way, we can use our existing Python-based logic and reporting engines on the Ghidra platform.
It would be the best of both worlds.


## research goal: is it feasible to extend Ghidra with Python 3.8?

You'd think if it could be done, someone would have already done it.
So, that's not very promising.

In any case, let's figure out why, and then answer the following:

  - What is the easiest way to extend Ghidra such that I can run modern Python scripts to access analysis results?
  - Does this require source code changes to core Ghidra? (wanted: no)
  - Can this be done strictly within an extension? (wanted: yes)
  - How can the script access analysis results? (required)
  - Can a script extend the user interface? (desirable?)

I have at least one idea, so let's get that on paper below.


## strategy: pass JNI environment to a Python interpreter

### first, Ghidra supports JNI

Ghidra runs on the JVM, which supports JNI, a standardized interop layer.

Using JNI, the JVM can dynamically load a native library (e.g. `.so` or `.dll`) and invoke specially formed exports.
For example, in Java:

```java
public class JNIExample {
   static {
      System.loadLibrary("myjni"); // myjni.dll (Windows) or libmyjni.so (Unixes)
   }
 
   // Native method that converts the given int to an Integer instance.
   private native Integer toInteger(int number);
 
   public static void main(String args[]) {
      JNIExample obj = new JNIExample();
      System.out.println("In Java, the number is :" + obj.toInteger(9999));
   }
}
```
[source](https://www3.ntu.edu.sg/home/ehchua/programming/java/JavaNativeInterface.html#zz-6.1)

The native routine receives a pointer to the JNI environment.
The environment is a structure with a well-defined layout that contains function pointers that can manipulate the JVM.
Oracle documents the layout of the "Interface Function Table" in the 
 [spec on their website](https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/functions.html).
Ultimately, the native routine can index into the structure and invoke functions to lookup Java classes, call instance methods, access object properties, etc. via reflection.
For example, in C:

```c
#include <jni.h>
#include <stdio.h>
#include "JNIExample.h"
 
JNIEXPORT jobject JNICALL
Java_JNIExample_toInteger (JNIEnv *env, jobject thisObj, jint number) {

   // Get a class reference for java.lang.Integer
   jclass cls = (*env)->FindClass(env, "java/lang/Integer");
 
   // Get the Method ID of the constructor which takes an int
   jmethodID init = (*env)->GetMethodID(env, cls, "<init>", "(I)V");
   if (NULL == init) return NULL;

   // Allocate a new instance, with an int argument
   jobject obj = (*env)->NewObject(env, cls, init, number);
 
   // Try running the toString() on this newly create object
   jmethodID toString = (*env)->GetMethodID(env, cls, "toString", "()Ljava/lang/String;");
   if (NULL == toString) return NULL;

   // here's a native representation of the string
   jstring str = (*env)->CallObjectMethod(env, obj, toString);
   const char *cstr = (*env)->GetStringUTFChars(env, str, NULL);
   printf("In C: the number is %s\n", cstr);
   // TODO: really need to call `releaseStringUTFChars` to free this string, sorry!

   return obj;
}
```
[source](https://www3.ntu.edu.sg/home/ehchua/programming/java/JavaNativeInterface.html#zz-6.1)


The takeaway: Ghidra extensions can load native libraries that implement some/all of the functionality.

Note, I'm not the first to think of this:
in [this issue](https://github.com/NationalSecurityAgency/ghidra/issues/175), the Ghidra developers explain why they discourage the use of JNI:

> We advise against using JNI when developing extensions for a couple of reasons.
> First, if there is a problem in an extension's native code, we don't want it to bring down the entire Ghidra process.
> Second, Ghidra discovers extensions at runtime and adds them to the classpath,
>  but it cannot add native libraries to the process's library search path at runtime for all supported platforms.
> That would require a custom launch script which would be tough to distribute generically.
>
> The decompiler and other native executables also benefit from the process isolation I mentioned above,
> at hopefully a lost cost in resources on modern hardware.

We need to ensure these tradeoffs are understood and acceptable.
The key points seem to be:
  - isolation, and
  - ease of distribution


### second, JNI native library can link against modern Python

Native libraries can link against (either statically or dynamically) `python38.so|dll` and host a modern Python interpreter.
This is well documented on [the Python website](https://docs.python.org/3/extending/embedding.html).

The native library would typically do the following steps:

  1. create an interpreter
  2. configure the interpreter (set limits, install directory, etc.)
  3. inject any callbacks available to python-land (e.g. `idc` in IDAPython)
  4. invoke Python code, either via:
      - eval a string, or
      - run a file
  5. and then: the Python code may call back into the native library via a callback, or finish and exit

Here's the Hello World example from [python.org](https://docs.python.org/3/extending/embedding.html):

```c
#define PY_SSIZE_T_CLEAN
#include <Python.h>

int
main(int argc, char *argv[])
{
    Py_Initialize();

    PyRun_SimpleString("from time import time,ctime\n"
                       "print('Today is', ctime(time()))\n");

    if (Py_FinalizeEx() < 0) {
        exit(120);
    }

    return 0;
}
```

The takeaway: Ghidra extensions can load native libraries that run a modern Python interpreter.
But, how can Python reach into Ghidra?


### third, Python can interop with native routines (via ctypes)

There are Python libraries that enable the interop between Python and native code.

`ctypes` is a popular choice.
It can (de)serialize Python objects into native representations (e.g. `int` to little-endian uint32 and `bool` to uint8) and call native routines.
Therefore, if you have a well-defined layout, Python can read, write, and invoke native code/data.

JNI has a well-defined layout, so I think we can use `ctypes` to call functions that manipulate a JVM.


### therefore...

A Ghidra extension can load a native library that hosts a modern Python interpreter that can call back into the JVM via JNI and reflection.

The native library must pass the JNI environment pointer into the Python interpreter.
Code within the interpreter uses `ctypes` to access appropriate fields of the JNI environment.
This would enable Python scripts to fetch data from Ghidra's analysis.

The [karpierz/jni](https://github.com/karpierz/jni/blob/master/src/jni/ctypes/__init__.py) project demonstrates how to use `ctypes` to interact via JNI.
For example:

```python
def test_string_method(self):
    """A Java string can be created, and the content returned"""

    # This string contains unicode characters
    s = "Woop"
    java_string = self.jenv.NewStringUTF(s.encode("utf-8"))

    Example = self.jenv.FindClass(b"org/jt/jni/test/Example")
    self.assertTrue(Example)

    # Find the default constructor
    Example__init = self.jenv.GetMethodID(Example, b"<init>", b"()V")
    self.assertTrue(Example__init)

    # Find the Example.duplicate_string() method on Example
    Example__duplicate_string = self.jenv.GetMethodID(Example, b"duplicate_string", b"(Ljava/lang/String;)Ljava/lang/String;")
    self.assertTrue(Example__duplicate_string)

    # Create an instance of org.jt.jni.test.Example using the default constructor
    obj1 = self.jenv.NewObject(Example, Example__init)
    self.assertTrue(obj1)

    # Invoke the string duplication method
    jargs = jni.new_array(jni.jvalue, 1)
    jargs[0].l = java_string
    result = self.jenv.CallObjectMethod(obj1, Example__duplicate_string, jargs)
    self.assertEqual(self.jstring2unicode(jni.cast(result, jni.jstring)), "WoopWoop")
```
[source](https://github.com/karpierz/jni/blob/master/tests/python/test_jni.py)

Fetching data from Ghidra via JNI & `ctypes` probably wouldn't look pretty, as there would be lots of reflection.
But, its feasible to build up wrappers that hide the reflection calls.
Jython does something like this.


### easy mode: Jep?

A [colleague](https://twitter.com/mehunhoff) points out the [ninia/jep](https://github.com/ninia/jep) project that may provide a lot of the necessary infrastructure:

> Jep embeds CPython in Java through JNI.
>
> Notable features
>
>  - Interactive Jep console much like Python's interactive console
>  - Supports multiple, simultaneous, mostly sandboxed sub-interpreters or shared interpreters
>  - Numpy support for Java primitive arrays

This sounds like points one and two above.

I think we could use the JARs provided via Maven in the Ghidra extension to create the Python interpreter and invoke scripts.
Jep even provides [object wrappers](https://github.com/ninia/jep/wiki/How-Jep-Works#objects) that should make it easy to manipulate Java objects.

Primary difficulty here is probably how to build and distribute the plugin;
however, this is something we'd have to do anyways, so by using Jep, we can jump right to that step.
