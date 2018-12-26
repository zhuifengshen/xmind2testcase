#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
testlink.testlink
"""


class TestSuite(object):

    def __init__(self, name='', details='', testcase_list=None, sub_suites=None):
        """
        TestSuite (TODO(devin): there is an infinite recursive reference problem with initializing an empty list)
        :param name: test suite name
        :param details: test suite detail infomation
        :param testcase_list: test case list
        :param sub_suites: sub test suite list
        """
        self.name = name
        self.details = details
        self.testcase_list = testcase_list
        self.sub_suites = sub_suites

    def to_dict(self):
        data = {
            'name': self.name,
            'details': self.details,
            'testcase_list': [],
            'sub_suites': []
        }

        if self.sub_suites:
            for suite in self.sub_suites:
                data['sub_suites'].append(suite.to_dict())

        if self.testcase_list:
            for case in self.testcase_list:
                data['testcase_list'].append(case.to_dict())

        return data


class TestCase(object):

    def __init__(self, name='', version=1, summary='', preconditions='', execution_type=1, importance=2, estimated_exec_duration=3, status=7, steps=None):
        """
        TestCase
        :param name: test case name
        :param version: test case version infomation
        :param summary: test case summary infomation
        :param preconditions: test case pre condition
        :param execution_type: manual or automate
        :param importance: high:1, middle:2, low:3
        :param estimated_exec_duration: estimated execution duration
        :param status: draft:1, ready ro review:2, review in progress:3, rework:4, obsolete:5, future:6, final:7
        :param steps: test case step list
        """
        self.name = name
        self.version = version
        self.summary = summary
        self.preconditions = preconditions
        self.execution_type = execution_type
        self.importance = importance
        self.estimated_exec_duration = estimated_exec_duration
        self.status = status
        self.steps = steps

    def to_dict(self):
        data = {
            'name': self.name,
            'version': self.version,  # TODO(devin): get version content
            'summary': self.summary,
            'preconditions': self.preconditions,
            'execution_type': self.execution_type,
            'importance': self.importance,
            'estimated_exec_duration': self.estimated_exec_duration,  # TODO(devin): get estimated content
            'status': self.status,  # TODO(devin): get status content
            'steps': []
        }

        if self.steps:
            for step in self.steps:
                data['steps'].append(step.to_dict())

        return data


class TestStep(object):

    def __init__(self, step_number=1, actions='', expectedresults='', execution_type=1):
        """
        TestStep
        :param step_number: test step number
        :param actions: test step actions
        :param expectedresults: test step expected results
        :param execution_type: test step execution type
        """
        self.step_number = step_number
        self.actions = actions
        self.expectedresults = expectedresults
        self.execution_type = execution_type  # TODO(devin): get execution type content

    def to_dict(self):
        data = {
            'step_number': self.step_number,
            'actions': self.actions,
            'expectedresults': self.expectedresults,
            'execution_type': self.execution_type
        }
        return data

