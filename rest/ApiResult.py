#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import jsonify

import traceback


class ApiResult:

    def __init__(self, data, status=0, message='ok'):
        self.data = data
        self.status = status
        self.message = message

    def to_json(self):
        return jsonify(self.__dict__)


def error_message(message):
    return ApiResult(None, -1, message).to_json()


def error():
    return ApiResult(None, -1, traceback.format_exc())
    # exc_type, exc_value, exc_traceback = sys.exc_info()
    # return ApiResult(None, -1, repr(traceback.format_exception(exc_type, exc_value,
    #                                       exc_traceback)))


def success(data):
    return ApiResult(data)
