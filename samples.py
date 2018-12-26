#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
from testcase.zentao import xmind_to_zentao_csv_file
from testcase.testlink import xmind_to_testlink_xml_file
from testcase.utils import xmind_testcase_to_json_file, get_xmind_testcase_dict_data_list, \
    get_xmind_testsuite_dict_data_list, xmind_testsuite_to_json_file


def main():
    xmind_file = 'docs/xmind_testcase_template.xmind'
    print('Start to convert XMind file: %s' % xmind_file)

    zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
    print('Convert XMind file to zentao csv file successfully: %s' % zentao_csv_file)

    testlink_xml_file = xmind_to_testlink_xml_file(xmind_file)
    print('Convert XMind file to testlink xml file successfully: %s' % testlink_xml_file)

    testsuite_json_file = xmind_testsuite_to_json_file(xmind_file)
    print('Convert XMind file to testsuite json file successfully: %s' % testsuite_json_file)

    testcase_json_file = xmind_testcase_to_json_file(xmind_file)
    print('Convert XMind file to testcase json file successfully: %s' % testcase_json_file)

    testsuites = get_xmind_testsuite_dict_data_list(xmind_file)
    print('Convert XMind to testsuits dict data:\n%s' % json.dumps(testsuites, indent=4, separators=(',', ': ')))

    testcases  = get_xmind_testcase_dict_data_list(xmind_file)
    print('Convert Xmind to testcases dict data:\n%s' % json.dumps(testcases, indent=4, separators=(',', ': ')))

    print('Finished conversion, Congratulations!')


if __name__ == '__main__':
    main()
