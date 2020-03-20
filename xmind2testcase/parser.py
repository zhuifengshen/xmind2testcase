#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import logging
from xmind2testcase.metadata import TestSuite, TestCase, TestStep

config = {'sep': ' ',
          'valid_sep': '&>+/-',
          'precondition_sep': '\n----\n',
          'summary_sep': '\n----\n',
          'ignore_char': '#!！'
          }


def xmind_to_testsuites(xmind_content_dict):
    """convert xmind file to `xmind2testcase.metadata.TestSuite` list"""
    suites = []

    for sheet in xmind_content_dict:
        logging.debug('start to parse a sheet: %s', sheet['title'])
        root_topic = sheet['topic']
        sub_topics = root_topic.get('topics', [])

        if sub_topics:
            root_topic['topics'] = filter_empty_or_ignore_topic(sub_topics)
        else:
            logging.warning('This is a blank sheet(%s), should have at least 1 sub topic(test suite)', sheet['title'])
            continue
        suite = sheet_to_suite(root_topic)
        # suite.sheet_name = sheet['title']  # root testsuite has a sheet_name attribute
        logging.debug('sheet(%s) parsing complete: %s', sheet['title'], suite.to_dict())
        suites.append(suite)

    return suites


def filter_empty_or_ignore_topic(topics):
    """filter blank or start with config.ignore_char topic"""
    result = [topic for topic in topics if not(
            topic['title'] is None or
            topic['title'].strip() == '' or
            topic['title'][0] in config['ignore_char'])]

    for topic in result:
        sub_topics = topic.get('topics', [])
        topic['topics'] = filter_empty_or_ignore_topic(sub_topics)

    return result


def filter_empty_or_ignore_element(values):
    """Filter all empty or ignore XMind elements, especially notes、comments、labels element"""
    result = []
    for value in values:
        if isinstance(value, str) and not value.strip() == '' and not value[0] in config['ignore_char']:
            result.append(value.strip())
    return result


def sheet_to_suite(root_topic):
    """convert a xmind sheet to a `TestSuite` instance"""
    suite = TestSuite()
    root_title = root_topic['title']
    separator = root_title[-1]

    if separator in config['valid_sep']:
        logging.debug('find a valid separator for connecting testcase title: %s', separator)
        config['sep'] = separator  # set the separator for the testcase's title
        root_title = root_title[:-1]
    else:
        config['sep'] = ' '

    suite.name = root_title
    suite.details = root_topic['note']
    suite.sub_suites = []

    for suite_dict in root_topic['topics']:
        suite.sub_suites.append(parse_testsuite(suite_dict))

    return suite


def parse_testsuite(suite_dict):
    testsuite = TestSuite()
    testsuite.name = suite_dict['title']
    testsuite.details = suite_dict['note']
    testsuite.testcase_list = []
    logging.debug('start to parse a testsuite: %s', testsuite.name)

    for cases_dict in suite_dict.get('topics', []):
        for case in recurse_parse_testcase(cases_dict):
            testsuite.testcase_list.append(case)

    logging.debug('testsuite(%s) parsing complete: %s', testsuite.name, testsuite.to_dict())
    return testsuite


def recurse_parse_testcase(case_dict, parent=None):
    if is_testcase_topic(case_dict):
        case = parse_a_testcase(case_dict, parent)
        yield case
    else:
        if not parent:
            parent = []

        parent.append(case_dict)

        for child_dict in case_dict.get('topics', []):
            for case in recurse_parse_testcase(child_dict, parent):
                yield case

        parent.pop()


def is_testcase_topic(case_dict):
    """A topic with a priority marker, or no subtopic, indicates that it is a testcase"""
    priority = get_priority(case_dict)
    if priority:
        return True

    children = case_dict.get('topics', [])
    if children:
        return False

    return True


def parse_a_testcase(case_dict, parent):
    testcase = TestCase()
    topics = parent + [case_dict] if parent else [case_dict]

    testcase.name = gen_testcase_title(topics)

    preconditions = gen_testcase_preconditions(topics)
    testcase.preconditions = preconditions if preconditions else '无'

    summary = gen_testcase_summary(topics)
    testcase.summary = summary if summary else testcase.name
    testcase.execution_type = get_execution_type(topics)
    testcase.importance = get_priority(case_dict) or 2

    step_dict_list = case_dict.get('topics', [])
    if step_dict_list:
        testcase.steps = parse_test_steps(step_dict_list)

    # the result of the testcase take precedence over the result of the teststep
    testcase.result = get_test_result(case_dict['markers'])

    if testcase.result == 0 and testcase.steps:
        for step in testcase.steps:
            if step.result == 2:
                testcase.result = 2
                break
            if step.result == 3:
                testcase.result = 3
                break

            testcase.result = step.result  # there is no need to judge where test step are ignored

    logging.debug('finds a testcase: %s', testcase.to_dict())
    return testcase


def get_execution_type(topics):
    labels = [topic.get('label', '') for topic in topics]
    labels = filter_empty_or_ignore_element(labels)
    exe_type = 1
    for item in labels[::-1]:
        if item.lower() in ['自动', 'auto', 'automate', 'automation']:
            exe_type = 2
            break
        if item.lower() in ['手动', '手工', 'manual']:
            exe_type = 1
            break
    return exe_type


def get_priority(case_dict):
    """Get the topic's priority（equivalent to the importance of the testcase)"""
    if isinstance(case_dict['markers'], list):
        for marker in case_dict['markers']:
            if marker.startswith('priority'):
                return int(marker[-1])


def gen_testcase_title(topics):
    """Link all topic's title as testcase title"""
    titles = [topic['title'] for topic in topics]
    titles = filter_empty_or_ignore_element(titles)

    # when separator is not blank, will add space around separator, e.g. '/' will be changed to ' / '
    separator = config['sep']
    if separator != ' ':
        separator = ' {} '.format(separator)

    return separator.join(titles)


def gen_testcase_preconditions(topics):
    notes = [topic['note'] for topic in topics]
    notes = filter_empty_or_ignore_element(notes)
    return config['precondition_sep'].join(notes)


def gen_testcase_summary(topics):
    comments = [topic['comment'] for topic in topics]
    comments = filter_empty_or_ignore_element(comments)
    return config['summary_sep'].join(comments)


def parse_test_steps(step_dict_list):
    steps = []

    for step_num, step_dict in enumerate(step_dict_list, 1):
        test_step = parse_a_test_step(step_dict)
        test_step.step_number = step_num
        steps.append(test_step)

    return steps


def parse_a_test_step(step_dict):
    test_step = TestStep()
    test_step.actions = step_dict['title']

    expected_topics = step_dict.get('topics', [])
    if expected_topics:  # have expected result
        expected_topic = expected_topics[0]
        test_step.expectedresults = expected_topic['title']  # one test step action, one test expected result
        markers = expected_topic['markers']
        test_step.result = get_test_result(markers)
    else:  # only have test step
        markers = step_dict['markers']
        test_step.result = get_test_result(markers)

    logging.debug('finds a teststep: %s', test_step.to_dict())
    return test_step


def get_test_result(markers):
    """test result: non-execution:0, pass:1, failed:2, blocked:3, skipped:4"""
    if isinstance(markers, list):
        if 'symbol-right' in markers or 'c_simbol-right' in markers:
            result = 1
        elif 'symbol-wrong' in markers or 'c_simbol-wrong' in markers:
            result = 2
        elif 'symbol-pause' in markers or 'c_simbol-pause' in markers:
            result = 3
        elif 'symbol-minus' in markers or 'c_simbol-minus' in markers:
            result = 4
        else:
            result = 0
    else:
        result = 0

    return result








