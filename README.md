# jencrypt

File and directory encryption application with auto-mount volume for macOS. 

## Installation

```bash
$ brew install JamesZBL/jencrypt/jencrypt
```

If you dont' have ``homebrew`` installed, see [here](https://brew.sh)


## Usage

```bash
$ jencrypt
```


## Functions

```
0. Exit.
1. Mount encrypted volume.
2. Wipe all encrypted data.
3. Show status.
```

## Example

After successfully installed ``jencrypt``, you should execute the ``jencrypt`` command in Terminal 
 or 3rd party terminal, eg: iTerm2.
 
It'll show function list.

Select 1.

Input your password for encryption. It's now allowed to change password in current version.
Please input carefully.

After typing password, press ``Enter``. Open ``Finder.app``. You will see a new volume named
``jencrypt-xxx``, open it and put files or folders into it. 

When you don't need edit or view these private files anymore, press ``ctrl-C`` to exit ``jencrypt``.
The encrypted volume will be ejected automatically. Or, you can eject the private volume manually, after that
, ``jencrypt`` will also exit automatically.
