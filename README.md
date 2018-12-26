# xmind2testcase

**xmind2testcase** 工具提供了一个高效测试用例设计的解决方案！

软件质量测试过程中，最重要、最核心就是测试用例的设计，也是测试童鞋、测试团队日常投入最多时间的工作内容之一。

然而，传统的测试用例设计过程有很多痛点：
- 1、使用Excel表格进行测试用例设计，虽然成本低，但版本管理麻烦，维护更新耗时，用例评审繁琐，执行情况报表统计难...
- 2、使用TestLink、TestCenter、Redmine等传统测试管理工具，虽然测试用例的执行、管理、统计比较方便，但依然存在编写用例效率不高、思路不够发散、在产品快速迭代过程中比较耗时...
- 3、公司自研测试管理工具，这是个不错的选择，但对于大部分小公司、小团队，一方面研发维护成本高，另一方面对技术要有一定要求...
- 4、...


基于以上情况，现在越来越多公司选择使用**思维导图**这种高效的生产力工具进行用例设计，特别是敏捷开发团队。
事实上也证明，思维导图其发散性思维、图形化思维的特点，跟测试用例设计时所需的思维非常吻合，所以很大程度上提升了我们测试用例设计的效率，也极大方便测试用例评审。
但是与此同时，使用思维导图进行测试用例设计也带来不少问题：
- 1、测试用例难以量化管理、执行情况难以统计；
- 2、测试用例执行结果与BUG管理系统难以打通；
- 3、团队成员用思维导图设计用例的风格各异，沟通成本巨大；
- 4、...

综上，我们可以发现不同的测试用例设计方式，各有各个的优劣。那么问题来了，我们能不能将它们各自优点合在一起呢？这样不就可以提升我们的效率了！

于是，这时候 **xmind2testcase** 就应运而生了，该工具基于 Python 实现，通过制定**测试用例通用模板**，
然后使用 **[XMind](https://www.xmind.cn/)** 这款开源且广为流传的思维导图工具进行用例设计。
制定**测试用例通用模板**是其中一个非常核心的步骤（下文有相关介绍），这样接下来我们就可以根据**测试用例通用模板**，在 XMind 文件上解析并提取出测试用例所需的基本信息，
然后合成常见**测试用例管理系统**中**用例导入文件**所需的格式即可。

当前 **xmind2testcase** 已实现从 XMind 文件到 TestLink 和 Zentao(禅道) 两大常见用例管理系统的测试用例转换，同时也提供 XMind 文件解析后的两种数据接口
（TestSuite、TestCase两种级别的JSON数据），方便快速与其他测试用例管理系统打通。


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