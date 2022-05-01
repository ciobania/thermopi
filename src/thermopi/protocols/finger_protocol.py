#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# author: 'ACIOBANI'
# from twisted.internet import protocol
from twisted.protocols import basic


class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        print(user, dir(user))
        deferred = self.factory.get_user(user)

        def onError(err):
            return "Internal server error"
        deferred.addErrback(onError)

        def writeResponse(message):
            self.transport.write(message + b"\r\n")
            self.transport.loseConnection()
        deferred.addCallback(writeResponse)
