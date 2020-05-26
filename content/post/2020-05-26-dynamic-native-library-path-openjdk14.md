---
title: "Dynamic native library search path on OpenJDK14"
date: 2020-05-26T00:00:00-07:00
draft: false
---

Braindump on changing the Java native library search path (typically set via `java.library.path`) at runtime on OpenJDK 14.
The JRE parses and initializes the configuration once upon startup, so subsequent calls to `System.setProperty("java.library.path", ...)` have no effect.
As a workaround, we can use reflection to update the internal datastructures with our extended search path.

Internet comments suggest this should work for JDK 12 and 13.
For Java 8 and earlier, you can try [this techinque](https://stackoverflow.com/a/49226657/87207).

This approach will not work in JDK 15, as the internal data structures have changed.
Also, the reflection tricks happening here [will probably be rejected](http://mail.openjdk.java.net/pipermail/jigsaw-dev/2017-May/012673.html) in future Java releases.

The *right* way to do this is to set the path at JVM startup.

References:
  - http://fahdshariff.blogspot.com/2011/08/changing-java-library-path-at-runtime.html
  - https://stackoverflow.com/a/59468135/87207
  - https://github.com/openjdk/jdk/blob/4b7bbaf5b001c17e3bcd8d8ec7e4cb2d66e795e5/src/java.base/share/classes/java/lang/ClassLoader.java#L2629


#### `DynamicLibraryFoo.java`

```java
/**
 * Here is a demonstration of changing the native library search path (`java.library.path`) at runtime.
 * It uses reflection to manipulate internal data strcutures, so its not portable.
 * This technique was developed and works on OpenJDK 14.
 * 
 * This Java program loads a native library named `foo` from the directory given as the first CLI argument.
 * 
 * Steps:
 *   1. generate native library headers: javac ./DynamicLibraryFoo.java -h .
 *   2. compile native libary:
 *      gcc DynamicLibraryFoo.cpp                               \
 *        -I /usr/lib/jvm/java-14-openjdk-amd64/include         \
 *        -I /usr/lib/jvm/java-14-openjdk-amd64/include/linux/  \
 *        -shared 
 *        -o libfoo.so
 *   3. package JAR: jar cf DynamicLibraryFoo.jar DynamicLibraryFoo.class
 *   4. invoke program: java -cp DynamicLibraryFoo.jar DynamicLibraryFoo .
 */

import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodHandles.Lookup;
import java.lang.invoke.MethodType;
import java.lang.invoke.VarHandle;

public class DynamicLibraryFoo {
	public native int random();
	
	/**
	 * prepend the native library search path with the given path.
	 * undo this operation with `popLibraryPath()`.
	 * this uses reflection to manipulate internal data structures, and is not portable.
	 */
	private static void pushLibraryPath(String path) throws IllegalAccessException, NoSuchFieldException, Exception {
		// this routine will NOT work on java master, from at least Mar 12, 2020 onwards:
		// https://github.com/openjdk/jdk/commit/d5d6dc0caa1d2db6e85b3fe979ae7a204678de57#diff-0ed25ca0c4147559231b206fdaaa5a00
		//
		// for PoC, support only OpenJDK 14
		if (!System.getProperty("java.version").startsWith("14.")) {
			throw new Exception("unsupported java version");
		}

		// derived from: https://stackoverflow.com/a/59468135/87207
		// given the comments in the thread, this technique should probably work on JVMs earlier than OpenJDK 14.
		Lookup cl = MethodHandles.privateLookupIn(ClassLoader.class, MethodHandles.lookup());
		VarHandle usr_paths = cl.findStaticVarHandle(ClassLoader.class, "usr_paths", String[].class);
		String[] existing_paths = (String[])(usr_paths.get());
		
		String[] new_paths = new String[existing_paths.length + 1];
		new_paths[0] = path;
		for (var i = 0; i < existing_paths.length; i++) {
			new_paths[i + 1] = existing_paths[i];
		}
		usr_paths.set(new_paths);
	}
	
	/**
	 * remove the first entry of the native library search path.
	 * this uses reflection to manipulate internal data structures, and is not portable.
	 */
	private static String popLibraryPath() throws IllegalAccessException, NoSuchFieldException, Exception {
		// this routine will NOT work on java master, from at least Mar 12, 2020 onwards:
		// https://github.com/openjdk/jdk/commit/d5d6dc0caa1d2db6e85b3fe979ae7a204678de57#diff-0ed25ca0c4147559231b206fdaaa5a00
		//
		// for PoC, support only OpenJDK 14
		if (!System.getProperty("java.version").startsWith("14.")) {
			throw new Exception("unsupported java version");
		}

		// derived from: https://stackoverflow.com/a/59468135/87207
		Lookup cl = MethodHandles.privateLookupIn(ClassLoader.class, MethodHandles.lookup());
		VarHandle usr_paths = cl.findStaticVarHandle(ClassLoader.class, "usr_paths", String[].class);
		String[] existing_paths = (String[])(usr_paths.get());
		
		String[] new_paths = new String[existing_paths.length - 1];
		for (var i = 0; i < existing_paths.length; i++) {
			new_paths[i] = existing_paths[i + 1];
		}
		usr_paths.set(new_paths);

		return existing_paths[0];
	}

	public static void main(String[] args) throws IllegalAccessException, NoSuchFieldException, Exception {
		System.out.println("hello");
		
		// the first CLI argument specifies the directory in which we'll find the `libfoo.so`.
		String path = args[0];
		System.out.println("native library path: " + path);

		// update the native library path, load the library, and revert the path.
		pushLibraryPath(path);
		System.loadLibrary("foo");
		assert popLibraryPath() == path;

		// demonstrate the native library works
		DynamicLibraryFoo foo = new DynamicLibraryFoo();
		assert foo.random() == 42;
		System.out.println("the library works");

		System.out.println("goodbye");
	}
}

```

#### `DynamicLibraryFoo.cpp`

```c
#include "DynamicLibraryFoo.h"

JNIEXPORT jint JNICALL Java_DynamicLibraryFoo_random
(JNIEnv* env, jobject obj) {
    return 42;
}
```

#### output

```
user@hostname$ javac DynamicLibraryFoo.java && jar cf DynamicLibraryFoo.jar DynamicLibraryFoo.class                                                                                            1
user@hostname$ java -cp DynamicLibraryFoo.jar DynamicLibraryFoo .
hello
native library path: .
WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access using Lookup on DynamicLibraryFoo (file:./DynamicLibraryFoo.jar) to class java.lang.ClassLoader
WARNING: Please consider reporting this to the maintainers of DynamicLibraryFoo
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
the library works
goodbye
```

So, it works, but you're not supposed to do it.
