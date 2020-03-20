#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import logging
import sys
from xmind2testcase.zentao import xmind_to_zentao_csv_file
from xmind2testcase.testlink import xmind_to_testlink_xml_file
from xmind2testcase.utils import get_absolute_path, xmind_testcase_to_json_file
from webtool.application import launch

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(name)s  %(levelname)s  [%(module)s - %(funcName)s]: %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

using_doc = """
    Xmind2Testcase is a tool to parse xmind file into testcase file, which will help you generate a testlink recognized
    xml file or a zentao recognized cvs file, then you can import it into testlink or zentao.
    
    Usage:
     xmind2testcase [path_to_xmind_file] [-csv] [-xml] [-json]
     xmind2testcase [webtool] [port_num]
    
    Example:
     xmind2testcase /path/to/testcase.xmind        => output testcase.csv、testcase.xml、testcase.json
     xmind2testcase /path/to/testcase.xmind -csv   => output testcase.csv
     xmind2testcase /path/to/testcase.xmind -xml   => output testcase.xml
     xmind2testcase /path/to/testcase.xmind -json  => output testcase.json
     xmind2testcase webtool                        => launch the web testcase conversion tool locally: 127.0.0.1:5001
     xmind2testcase webtool 8000                   => launch the web testcase conversion tool locally: 127.0.0.1:8000
    """


def cli_main():
    if len(sys.argv) > 1 and sys.argv[1].endswith('.xmind'):
        xmind_file = sys.argv[1]
        xmind_file = get_absolute_path(xmind_file)
        logging.info('Start to convert XMind file: %s', xmind_file)

        if len(sys.argv) == 3 and sys.argv[2] == '-json':
            testlink_json_file = xmind_testcase_to_json_file(xmind_file)
            logging.info('Convert XMind file to testcase json file successfully: %s', testlink_json_file)
        elif len(sys.argv) == 3 and sys.argv[2] == '-xml':
            testlink_xml_file = xmind_to_testlink_xml_file(xmind_file)
            logging.info('Convert XMind file to testlink xml files successfully: %s', testlink_xml_file)
        elif len(sys.argv) == 3 and sys.argv[2] == '-csv':
            zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
            logging.info('Convert XMind file to zentao csv file successfully: %s', zentao_csv_file)
        else:
            testlink_json_file = xmind_testcase_to_json_file(xmind_file)
            testlink_xml_file = xmind_to_testlink_xml_file(xmind_file)
            zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
            logging.info('Convert XMind file successfully: \n'
                         '1、 testcase json file(%s)\n'
                         '2、 testlink xml file(%s)\n'
                         '3、 zentao csv file(%s)',
                         testlink_json_file,
                         testlink_xml_file,
                         zentao_csv_file)
    elif len(sys.argv) > 1 and sys.argv[1] == 'webtool':
        if len(sys.argv) == 3:
            try:
                port = int(sys.argv[2])
                launch(port=port)
            except ValueError:
                launch()
        else:
            launch()

    else:
        print(using_doc)


if __name__ == '__main__':
    cli_main()
