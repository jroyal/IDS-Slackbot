__author__ = 'jhroyal'

from rtcclient import RTCClient


def test3():
    rtc = RTCClient()
    rtc.getWorkItem(43746)

if __name__ == '__main__':
    test3()