+++
title = "Using a virtualenv for IDAPython"
slug = ""
description = ""
tags = ["ida", "python"]
date = 2025-03-25T09:38:32+01:00
+++

I like to use a separate virtual environment for each of my Python projects and workspaces.
This lets me isolate the packages and dependencies that I install,
 preventing versioning conflicts and generally keeping things more tidy.
When I use IDA, I'd also like IDAPython to use packages from a dedicated virtualenv,
 rather than the system-wide configuration.

First, I create a virtualenv in a well-known location;
I use `$IDAUSR` as a common place to put my IDA stuff:

```
$ python -m virtualenv ~/.idapro/venv
# or:
$ uv venv --seed ~/.idapro/venv
```

Now we need IDA to load this environment, rather than the global one.

#### Option 1: Open IDA with an already activated environment

If you lauch IDA with an environment already activated, it will stay in effect:

```
$ source ~/.idapro/venv/bin/activate.fish
$ ~/software/ida/ida
```

Then you'll see the following in the IDA output pane:

```
IDAPython: Requested to use virtual environment interpreter at ~/.idapro/venv/bin/python3
```

The downside is that you have to remember to activate the environment every time,
 and that this doesn't work with starting the application via the system menu, etc.

Note: I'm not quite sure how IDA detects the "virtual environment interpreter", and this makes me think that perhaps
 we could just set the `$VIRTUAL_ENV` environment variable prior to launching IDA.
I haven't tried this yet, because as just mentioned, its a little tough to only set the variable when launching IDA.


#### Option 2: Activate the environment from idapythonrc.py

`idapythonrc.py` is an IDAPython-specific configuration file loaded when Python is first initialized upon IDA startup.
Therefore, we can use this file to activate the virtual environment.

We can add the following to `$IDAUSR/idapythonrc.py`:

```python
# via: https://github.com/eset/ipyida/blob/master/README.virtualenv.adoc
def activate_virtualenv(virtualenv_path: Path):
    for bindir in ("Scripts", "bin"):
        activate_this_path = virtualenv_path / bindir / "activate_this.py"

        if not activate_this_path.exists():
            continue

        if not activate_this_path.is_file():
            continue

        exec(activate_this_path.read_text(), dict(__file__=str(activate_this_path)))
        print("activated virtual environment: " + str(virtualenv_path))
        break

    else:
        raise ValueError('Could not find "activate_this.py" in ' + str(virtualenv_path))


IDAUSR = Path(idaapi.get_user_idadir())
activate_virtualenv(IDAUSR / "venv")
```
Remember, ([`$IDAUSR` is usually `~/.idapro`](https://hex-rays.com/blog/igors-tip-of-the-week-33-idas-user-directory-idausr)).

The `activate_this.py` file is documented here: [Using Virtualenv without `bin/python`](https://virtualenv.pypa.io/en/legacy/userguide.html#using-virtualenv-without-bin-python):

> Luckily, it’s easy. You must use the custom Python interpreter to install libraries.
> But to use libraries, you just have to be sure the path is correct.
> A script is available to correct the path. You can setup the environment like:
> 
> ```
> activate_this = '/path/to/env/bin/activate_this.py'
> exec(open(activate_this).read(), {'__file__': activate_this})
> ```
>
> This will change sys.path and even change sys.prefix, but also allow you to use an existing interpreter.
> Items in your environment will show up first on sys.path, before global items.
> However, global items will always be accessible
> (as if the --system-site-packages flag had been used in creating the environment, whether it was or not).
> Also, this cannot undo the activation of other environments, or modules that have been imported.
> You shouldn’t try to, for instance, activate an environment before a web request;
> you should activate one environment as early as possible, and not do it again in that process.

I think you should also try to match the Python version used by the virtual environment with the IDAPython python version,
 so there's no weirdness with native libraries or interpreter incompatibilities or something:

```
$ uv python install 3.12
$ uv python list
...
cpython-3.12.7-macos-aarch64-none    ~/.local/share/uv/python/cpython-3.12.7/bin/python3.12
...
$ idapyswitch --force-path ~/.local/share/uv/python/cpython-3.12.7/lib/libpython3.12.dylib
```
I found I was not able to use `idapyswitch --force-path` directly with the virtual environment contents,
 because IDA wants to reference the Python interpreter shared library, but the virtualenv doesn't have a copy of it.

Anyways, with this onetime setup of your `idapythonrc.py`, you can keep an isolated space for IDAPython.
To install packages, you can either activate the environment (`source ~/.idapro/venv/bin/activate.fish`)
 or invoke pip directly: `~/.idapro/venv/bin/pip install foo`.


#### References:
  - https://github.com/Kerrigan29a/idapython_virtualenv
  - https://github.com/eset/ipyida/blob/master/README.virtualenv.adoc
