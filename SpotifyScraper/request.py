# -*- coding: utf-8 -*-

# Copyright 2020 Ali Akhtari <https://github.com/AliAkhtari78>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import requests


class Request:
    def __init__(self, cookie_file: str = None, headers: dict = None, proxy: dict = None):
        if cookie_file is None:
            self.cookie = None
        else:
            self.cookie_file = cookie_file
            try:
                self.cookie = self._parse_cookie_file()
            except:
                raise

        if headers is None:
            pass
            # self.headers = {
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            #     'Accept': '*/*',
            #     'DNT': '1',
            #     'app-platform': 'WebPlayer',
            # }
        else:
            self.headers = headers

        if proxy is None:
            self.proxy = None
        else:
            self.proxy = proxy

    def _parse_cookie_file(self) -> dict:
        """Parse a cookies.txt file and return a dictionary of key value pairs
        compatible with requests."""

        cookies = {}
        with open(self.cookie_file, 'r') as fp:
            for line in fp:
                if not re.match(r'^\#', line):
                    line_fields = line.strip().split('\t')
                    cookies[line_fields[5]] = line_fields[6]
        return cookies

    def request(self) -> requests.Session:
        """Create session using requests library and set cookie and headers."""

        request_session = requests.Session()
        # request_session.headers.update(self.headers)
        if self.cookie is not None:
            request_session.cookies.update(self.cookie)

        if self.proxy is not None:
            request_session.proxies.update(self.proxy)

        return request_session
