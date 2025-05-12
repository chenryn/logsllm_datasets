# Devops_Stackoverflow_summarization.jsonl 数据过滤计划

要求每一步骤都必须独立输出中间结果，并不能直接修改原始数据。

## 1. 数据预处理
[x] 1.1. 对问答对进行语义去重：利用SBERT/USE嵌入，识别并移除内容重复但表述不同的问答对(原始: 142731，去重后: 141996 个)。
[x] 1.2. 通过强相关的关键字，快速过滤出“日志/可观测性”强相关(8077 个)和“CI/CD”、“通用编程”强相关(61660 个)的问答对。
        “日志易/可观测性”强相关的关键字包括：
        LOG_KEYWORDS = {
            'log analysis', 'logstash', 'fluentd', 'rsyslog', 'sumologic',
            'elk', 'kibana', 'kusto', 'splunk', 'graylog', 'papertrail', 'loggly',
            'filebeat', 'observability', 'trace', 'tracing', 'open telemetry',
            'post-mortem', 'anomaly detection', 'prometheus', 'grafana',
            'root cause', 'troubleshooting', 'incident investigation',
            'nagios', 'zabbix', 'datadog', 'new relic', 'dynatrace', 'appdynamics'
        }
        "CI/CD"、“通用编程”强相关的关键字包括：
        CI_CD_KEYWORDS = {
            'ci/cd', 'continuous integration', 'continuous delivery', 'continuous deployment',
            'jenkins', 'travis', 'circleci', 'github actions', 'gitlab ci',
            'ide', 'unit test', 'test case', 'fullstack', 'database design', 'orm',
            'git commit', 'git push', 'pull request',
            'code review', 'refactoring', 'clean code', 'dynamic programming',
            'teamcity', 'bamboo', 'azure pipelines', 'bitbucket pipelines',
            'build automation', 'artifact repository', 'build artifact',
            'rollback', 'blue-green', 'canary', 'rollout', 'staging',
            'automate build', 'automate test', 'automation script', 'automation tool',
            'automate deployment', 'merge conflict', 'branch strategy', 'trunk-based'
        }

## 2. 核心过滤
[x] 2.1. 基于主题建模：使用主题建模算法（如BERTopic）识别与“日志/可观测性”相关的核心主题，并根据问答对在这些主题上的概率分布进行过滤。可以考虑使用其分层主题功能进行更精细的控制(从 8077 条数据的 128 个 topic 里过滤剩下 3028 个)。

## 3. 模型训练
[x] 3.1. 基于嵌入的分类：使用嵌入作为特征，训练一个分类器（如逻辑回归或小型神经网络），将问答对分为“日志/可观测性”(剩 2328 个)和“CI/CD”、“通用编程”(139668 个)两类。

