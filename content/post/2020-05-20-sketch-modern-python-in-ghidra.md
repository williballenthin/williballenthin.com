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

I would like to develop scripts in modern Python (e.g. 3.8) for Ghidra.


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

### first, Ghidra should support JNI

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
So, what do I want to do with that?


### second, JNI native library can link against modern Python

This is straightforward: native libraries can link against (either statically or dynamically) `python38.so|dll` and host a modern Python interpreter.

The native library can do the follow steps:

  1. create an interpreter
  2. configure the interpreter (set limits, install directory, etc.)
  3. inject any callbacks available to python-land (e.g. `idc` in IDAPython)
  4. invoke Python code, either via:
    a. eval a string, or
    b. run a file
  5. and then: the Python code may call back into the native library via a callback, or finish and exit

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

It probably wouldn't look pretty, as there would be lots of reflection.
But, its feasible to build up wrappers that hide the reflection calls.
Jython does something like this.
