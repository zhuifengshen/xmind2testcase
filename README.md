# xmind2testcase

**xmind2testcase** 提供了一个高效设计测试用例的解决方案！
基于 Python 实现，通过制定测试用例通用模板，然后借助 [XMind 思维导图](https://www.xmind.cn/)这款高效的生产力工具进行用例设计。
至此，核心步骤已完成，接下来便是根据测试用例通用模板，在 XMind 文件上提取测试用例所需的基本信息，然后转换为常见测试用例管理系统中**用例导入文件**所需格式即可。
在 xmind2testcase 中，目前以实现了 TestLink 和禅道两大常见用例管理系统的测试用例转换，同时提供了 XMind 文件解析后的 JSON 数据接口，以便简单快捷快速与转换为其他测试用例管理系统打通。


### 一、安装方式
```
pip3 install xmind2testcase
```

### 二、版本升级
```
pip3 install -U xmind2testcase
```

### 三、使用方式

#### 1、命令行调用
```
Usage:
 xmind2testcase [path_to_xmind_file] [-csv] [-xml] [-json]

Example:
 xmind2testcase /path/to/testcase.xmind        => output testcase.csv、testcase.xml、testcase.json
 xmind2testcase /path/to/testcase.xmind -csv   => output testcase.csv
 xmind2testcase /path/to/testcase.xmind -xml   => output testcase.xml
 xmind2testcase /path/to/testcase.xmind -json  => output testcase.json
```

#### 2、使用Web界面
```
Usage:
 xmind2testcase [webtool] [port_num]

Example:
 xmind2testcase webtool        => launch the web testcase convertion tool locally -> 127.0.0.1:5001
 xmind2testcase webtool 8000   => launch the web testcase convertion tool locally -> 127.0.0.1:8000
```

#### 3、API调用
```
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
    print('Finished Conversion, Congratulations!')


if __name__ == '__main__':
    main()
```

### 四、自动化发布：一键打 Tag 并上传至 PYPI 
每次在 __ about __.py 更新版本号后，运行以下命令，实现自动化更新打包上传至 [PYPI](https://pypi.org/) ，同时根据其版本号自动打 Tag 并推送到仓库：
```
python3 setup.py pypi
```


### 五、致谢
**xmind2testcase** 工具的产生，受益于以下四个开源项目，并在此基础上扩展、优化，受益匪浅，感恩！
- 1、**[XMind](https://github.com/zhuifengshen/xmind)**：XMind思维导图创建、解析、更新的一站式解决方案(Python实现)！  
- 2、**[xmind2testlink](https://github.com/tobyqin/xmind2testlink)**：践行了XMind通用测试用例模板设计思路，同时设计Web工具展示页面！
- 3、**[TestLink](http://www.testlink.org/)**：提供了完整的测试用例管理流程和文档；
- 4、**[禅道开源版(ZenTao)](https://www.zentao.net/)**：提供了完整的项目管理流程、文档和用户交流释疑群；

得益于开源，也将始终坚持开源，并为努力开源贡献自己的个人点滴之力。后续，将继续根据实际项目需要，定期进行维护更新和完善，欢迎大伙的使用和意见反馈，谢谢！

（如果本项目对你有帮助的话，也欢迎 _**star**_ ）