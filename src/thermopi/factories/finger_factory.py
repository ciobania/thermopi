#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
from twisted.internet import protocol, defer
from protocols.finger_protocol import FingerProtocol


class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, users):
        self.users = users

    def get_user(self, user):
        msg = "No such user `{}` found".format(user)
        return defer.succeed(self.users.get(user, bytes(msg.encode("UTF-8"))))
