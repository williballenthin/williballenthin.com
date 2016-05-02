---
layout: post
title: "How to install the Python package manager pip"
date: 2014-01-11 20:52
comments: false 
categories: python 
---

The [Python Package Index](https://pypi.python.org/pypi) (PyPI) is a 
repository of software for the Python programming language. 
[pip](https://pypi.python.org/pypi/pip) is
package manager for Python that manages the installation of modules
hosted on PyPI. I recommend using `pip` to install Python modules
over downloading the source directly because it also provides an easy
method to update and remove packages. Here I'll describe how to install
`pip` on various operating systems.


Basic `pip` Usage
-----------------

Install the two packages `python-registry` and `python-evtx`:

{% highlight sh %}
pip install python-registry python-evtx
{% endhighlight %}

Upgrade the two packages `python-registry` and `python-evtx`:

{% highlight sh %}
pip install --upgrade python-registry python-evtx
{% endhighlight %}

Remove the two previously installed packages `python-registry` and `python-evtx`:

{% highlight sh %}
pip uninstall python-registry python-evtx
{% endhighlight %}


Installing on Windows
---------------------
Christoph Gohlke prepares Windows installers for popular 
Python packages. He builds installers for Python 2 and 3, for
both 32-bit and 64-bit architectures. Pick and install the appropriate versions
of both the following two installers:

  - [setuptools](http://www.lfd.uci.edu/~gohlke/pythonlibs/#setuptools)
  - [pip](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)

Incidentally, I highly recommend these Windows installers for Python modules
that have a binary component, such as 
[lxml](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml).


Installing on Linux (Debian/Ubuntu)
-----------------------------------
Use `apt-get` to install `python-pip`:

{% highlight sh %}
sudo apt-get install python-pip
{% endhighlight %}


Installing on Linux (Fedora)
----------------------------
Use `yum` to install `python-pip`:

{% highlight sh %}
sudo yum install python-pip
{% endhighlight %}


Installing on Linux (Other)
---------------------------
Do the following two steps in order:

  1. Download and run the script [ez_setup.py](https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py)
  2. Download and run the script [get-pip](https://raw.github.com/pypa/pip/master/contrib/get-pip.py)


Installing on OSX (Homebrew)
----------------------------
`pip` is distributed with `python` when you install via `brew`:

{% highlight sh %}
brew install python
{% endhighlight %}


Installing on OSX (Other)
-------------------------
Install `pip` using `easy_install`, which should be included with `python`:

{% highlight sh %}
sudo easy_install python
{% endhighlight %}





