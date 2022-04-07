```
  ███                                                                                                         
 ░░░                                                                                                          
 ████  █████████████    ██████   ████████   █████  ████████  ████████   ██████   █████ ████  ██████  ████████ 
░░███ ░░███░░███░░███  ░░░░░███ ░░███░░███ ███░░  ░░███░░███░░███░░███ ░░░░░███ ░░███ ░███  ███░░███░░███░░███
 ░███  ░███ ░███ ░███   ███████  ░███ ░███░░█████  ░███ ░███ ░███ ░░░   ███████  ░███ ░███ ░███████  ░███ ░░░ 
 ░███  ░███ ░███ ░███  ███░░███  ░███ ░███ ░░░░███ ░███ ░███ ░███      ███░░███  ░███ ░███ ░███░░░   ░███     
 █████ █████░███ █████░░████████ ░███████  ██████  ░███████  █████    ░░████████ ░░███████ ░░██████  █████    
░░░░░ ░░░░░ ░░░ ░░░░░  ░░░░░░░░  ░███░░░  ░░░░░░   ░███░░░  ░░░░░      ░░░░░░░░   ░░░░░███  ░░░░░░  ░░░░░     
                                 ░███              ░███                           ███ ░███                    
                                 █████             █████                         ░░██████                     
                                ░░░░░             ░░░░░                           ░░░░░░                      
                                                                                                              
```

A simple IMAP password sprayer.

## Introduction

This tool performs password spraying against an IMAP server with support for SSL connections and socks proxy.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Requirements
Python 3.9 or later is necessary because of recent changes in `imaplib` built-in package.

### Installing

First, clone the repository

```
git clone https://github.com/yok4i/imapsprayer.git
```

Once inside it, run `poetry` to install the dependencies

```
poetry install
```

Alternatively, you can install them with `pip`

```
pip install -r requirements.txt
```

### Help

Use `-h` to show the help menu

```
poetry run ./imapsprayer -h

usage: imapsprayer.py [-h] -t TARGET [--port PORT] [--ssl] (-u USERNAME | -U FILE) (-p PASSWORD | -P FILE)
                      [-o OUTPUT] [-x PROXY] [--sleep SLEEP] [--jitter JITTER] --lockout LOCKOUT
                      [--timeout TIMEOUT] [--slack SLACK] [-s] [-v]

A simple IMAP password sprayer.

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        Target host (required)
  --port PORT           Target port (default 993 when using --ssl, 143 otherwise)
  --ssl                 Connect to server over an SSL encrypted socket
  -u USERNAME, --username USERNAME
                        Single username
  -U FILE, --usernames FILE
                        File containing usernames
  -p PASSWORD, --password PASSWORD
                        Single password
  -P FILE, --passwords FILE
                        File containing passwords
  -o OUTPUT, --output OUTPUT
                        Output file (default: valid_creds.txt)
  -x PROXY, --proxy PROXY
                        Proxy to pass traffic through: <scheme://ip:port>
  --sleep SLEEP         Sleep time (in seconds) between each iteration (default: 0)
  --jitter JITTER       Max jitter (in seconds) to be added to sleep time (default: 0)
  --lockout LOCKOUT     Lockout policy reset time (in minutes) (required)
  --timeout TIMEOUT     Socket timeout, in seconds (default: None)
  --slack SLACK         Slack webhook for sending notifications (default: None)
  -s, --shuffle         Shuffle user list
  -v, --verbose         Verbose output
```


## Examples

Test a single credential

```
poetry run ./imapsprayer.py -t imap.contoso.com -u me@contoso.com -p mypassword --lockout 1 --ssl --timeout 10
```

Perform password spraying using a proxy and waiting 30 minutes between each password iteration

```
poetry run ./imapsprayer.py -U emails.txt -P passwords.txt --proxy socks5://127.0.0.1:9050 --lockout 30
```

### Note

Only socks proxies supported.


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/yok4i/imapsprayer/tags). 


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


## Disclaimer

This tool is intended for educational purpose or for use in environments where you have been given explicit/legal authorization to do so.
