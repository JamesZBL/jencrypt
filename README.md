
<span style="display:block;text-align:center">![logo](logo.png)</span>

# jencrypt

![GitHub release (latest by date)](https://img.shields.io/github/v/release/jameszbl/jencrypt?label=RELEASE&style=flat-square&logo=github)
![Python version](https://img.shields.io/badge/python-%3E%3D3-green?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey?style=flat-square)
![GitHub](https://img.shields.io/github/license/jameszbl/jencrypt?color=orange&style=flat-square)


File and directory encryption application with auto-mount volume for macOS. 


Installation
--------

```bash
$ brew install JamesZBL/jencrypt/jencrypt
```

If you don't have ``homebrew`` installed, see [here](https://brew.sh)


Usage
--------

```bash
$ jencrypt
```


Functions
--------

```
0. Exit.
1. Mount encrypted volume.
2. Wipe all encrypted data.
3. Show status.
```


Example
--------

After successfully installed ``jencrypt``, you should execute the ``jencrypt`` command in Terminal 
 or 3rd party terminal, eg: iTerm2.
 
It'll show function list.

Select 1.

Input your password for encryption. It's not allowed to change password in current version.
Please input carefully.

After typing password, press ``Enter``. Open ``Finder.app``. You will see a new volume named
``jencrypt-xxx``, open it and put files or folders into it. 

When you don't need edit or view these private files anymore, press ``ctrl-C`` to exit ``jencrypt``.
The encrypted volume will be ejected automatically. Or, you can eject the private volume manually, after that
, ``jencrypt`` will also exit automatically.


Dependencies
------------

* Python 3
* [Watchdog](https://github.com/gorakhargosh/watchdog)
* openssl
* tar
* diskutil


Licensing
---------

Jencrypt is licensed under the terms of the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

Copyright 2021 [JamesZBL](https://github.com/JamesZBL).


Why Jencrypt?
------------

* AES-256 encryption
* Auto mount encryption volume
* Auto detect and re-encrypt
