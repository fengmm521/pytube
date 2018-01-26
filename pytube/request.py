# -*- coding: utf-8 -*-
"""Implements a simple wrapper around urlopen."""
from pytube.compat import urlopen
import os   
import time


def get(
    url=None, headers=False,
    streaming=False, chunk_size=8 * 1024,conRangefp = None
):
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :param bool headers:
        Only return the http headers.
    :param bool streaming:
        Returns the response body in chunks via a generator.
    :param int chunk_size:
        The size in bytes of each chunk.
    """
    response = None
    if streaming:
        import urllib2
        req = urllib2.Request(url) 
        if conRangefp:
            nfize = os.path.getsize(conRangefp)
            print conRangefp,nfize
            conRange = 'bytes=%d-'%(nfize)
            print conRange
            req.add_header('Range', conRange)
        try:
            response = urlopen(req)
            print '断点续传'
        except Exception as e:
            print e
            print '已超时'
            print response
    else:
        while True:
            try:
                response = urlopen(url)
                break
            except Exception as e:
                print '网络连接超时...5秒后重试'
                time.sleep(3)
            
    if streaming:
        return stream_response(response, chunk_size)
    elif headers:
        # https://github.com/nficano/pytube/issues/160
        return {k.lower(): v for k, v in response.info().items()}
    return (
        response
        .read()
        .decode('utf-8')
    )

import kthreadTimeoutTool

def stream_response(response, chunk_size=8 * 1024):
    """Read the response in chunks."""

    @kthreadTimeoutTool.timeoutTool(20)
    def slowFunc(response,chunk_size):
        try:
            buf = response.read(chunk_size)
        except Exception as e:

            return 'timeout'
        return buf

    while True:
        buf = slowFunc(response, chunk_size)
        if not buf:
            break
        elif buf == 'timeout':
            yield None
        yield buf


    # while True:
    #     print '1'
    #     buf = response.read(chunk_size)
    #     print '2'
    #     if not buf:
    #         break
    #     yield buf
