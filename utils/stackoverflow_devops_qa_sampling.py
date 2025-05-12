#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from typing import Dict, List, Set, Any
import argparse
from pathlib import Path
import ahocorasick

# 定义关键词集合
LOG_KEYWORDS = {
    # 日志管理相关词汇
    'log', 'logs', 'logging', 'logger', 'logfile', 'syslog', 'loglevel', 
    'logrotate', 'journalctl', 'eventlog', 'audit log', 'error log', 'log analysis',
    'log aggregation', 'log collection', 'log monitoring', 'log parser', 'log rotation',
    'log shipping', 'log storage', 'log viewer', 'logstash', 'fluentd', 'rsyslog',
    'elk', 'elasticsearch', 'kibana', 'kusto', 'splunk', 'graylog', 'papertrail', 'loggly',
    'filebeat', 'logback', 'log4j', 'nxlog', 'serilog', 'log format', 'structured logging',
    # 根因定位相关词汇
    'root cause', 'troubleshoot', 'troubleshooting', 'debug', 'debugging', 'diagnosis',
    'diagnostic', 'error', 'failure', 'crash', 'incident', 'investigation', 'analyze',
    'analysis', 'resolve', 'resolution', 'issue', 'problem', 'monitoring', 'alert',
    'alerting', 'observability', 'trace', 'tracing', 'profiling', 'performance issue',
    'bottleneck', 'latency', 'slowness', 'timeout', 'deadlock', 'memory leak',
    'exception', 'stack trace', 'core dump', 'crash report', 'post-mortem',
    'metrics', 'telemetry', 'symptom', 'anomaly', 'detection', 'prometheus', 'grafana',
    'nagios', 'zabbix', 'datadog', 'new relic', 'dynatrace', 'appdynamics'
}

# 要过滤掉的关键词
FILTER_KEYWORDS = {
    # 编程相关词汇
    'code', 'coding', 'algorithm', 'function', 'variable', 'class', 'object',
    'inheritance', 'method', 'property', 'api', 'sdk', 'library', 'framework',
    'syntax', 'compiler', 'interpreter', 'runtime', 'ide', 'editor', 'unit test',
    'test case', 'frontend', 'backend', 'fullstack', 'database design', 'orm',
    'data structure', 'algorithm', 'git commit', 'git push', 'pull request',
    'code review', 'refactoring', 'clean code', 'dynamic programming',
    # CI/CD 相关词汇
    'ci', 'cd', 'ci/cd', 'pipeline', 'jenkins', 'gitlab ci', 'github actions',
    'travis', 'circleci', 'teamcity', 'bamboo', 'azure pipelines', 'bitbucket pipelines',
    'build automation', 'continuous integration', 'continuous delivery',
    'continuous deployment', 'artifact repository', 'build artifact', 'release',
    'deployment', 'versioning', 'rollback', 'blue-green', 'canary', 'rollout',
    'staging', 'production', 'automate build', 'automate test',
    'automate deployment', 'merge conflict', 'branch strategy', 'trunk-based'
}

# 一些不应被过滤的例外情况
EXCEPTION_PHRASES = {
    'error code', 'error message', 'debug log', 'debug mode', 'debug level',
    'log message', 'deployment error', 'build error', 'release error', 
    'pipeline error', 'deployment failure', 'build failure'
}

# 构建Aho-Corasick自动机，用于高效匹配多个关键词
def build_automaton(keywords):
    """
    使用Aho-Corasick算法构建自动机，用于高效匹配多个关键词
    """
    automaton = ahocorasick.Automaton()
    for idx, key in enumerate(keywords):
        # 添加单词边界标记
        key_with_boundary = f' {key} '
        automaton.add_word(key_with_boundary, (idx, key))
    automaton.make_automaton()
    return automaton

# 全局变量，预处理关键词并构建自动机
LOG_KEYWORDS_AUTOMATON = build_automaton(LOG_KEYWORDS)
FILTER_KEYWORDS_AUTOMATON = build_automaton(FILTER_KEYWORDS)
STRONG_INDICATORS_AUTOMATON = build_automaton({'root cause', 'log analysis', 'troubleshooting', 'error log', 'incident investigation'})

def should_keep(text: str) -> bool:
    """
    判断一条记录是否应该保留
    
    - 如果包含日志管理或根因定位关键词，倾向于保留
    - 如果包含太多编程或CI/CD关键词，倾向于过滤掉
    - 如果同时包含两种关键词，基于比例来决定
    """
    
    # 将文本转为小写并添加空格以便于单词边界匹配
    text_lower = ' ' + text.lower() + ' '
    
    # 使用集合存储匹配的关键词
    log_rc_matches = set()
    filter_matches = set()
    
    # 使用Aho-Corasick自动机查找日志/根因关键词
    for _, (_, keyword) in LOG_KEYWORDS_AUTOMATON.iter(text_lower):
        log_rc_matches.add(keyword)
    
    # 使用Aho-Corasick自动机查找过滤关键词
    for _, (_, keyword) in FILTER_KEYWORDS_AUTOMATON.iter(text_lower):
        filter_matches.add(keyword)
    
    # 计数
    log_rc_count = len(log_rc_matches)
    filter_count = len(filter_matches)
    
    # 检查是否包含例外短语
    exception_match = any(f' {phrase} ' in text_lower for phrase in EXCEPTION_PHRASES)
    
    # 决策逻辑
    if log_rc_count > 0:
        if exception_match:
            return True
        
        # 如果日志/根因关键词数量明显多于过滤关键词，则保留
        if log_rc_count >= filter_count * 0.5:
            return True
        
        # 使用Aho-Corasick自动机检查是否包含强相关的日志/根因词汇
        strong_indicator_found = False
        for _ in STRONG_INDICATORS_AUTOMATON.iter(text_lower):
            strong_indicator_found = True
            break
        
        if strong_indicator_found:
            return True
    
    # 默认情况下过滤掉
    return False

def process_jsonl_file(input_path: str, output_path: str):
    """处理JSONL文件并保存筛选结果"""
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    kept_records = 0
    total_records = 0
    
    with open(input_file, 'r', encoding='utf-8') as in_f, \
         open(output_file, 'w', encoding='utf-8') as out_f:
        
        for line in in_f:
            total_records += 1
            
            try:
                record = json.loads(line.strip())
                
                # 确定判断的文本内容 - 可能需要根据实际JSON结构调整
                if isinstance(record, dict):
                    # 假设JSON包含question和answer字段
                    content_to_check = ""
                    if 'question' in record:
                        content_to_check += record['question'] + " "
                    if 'answer' in record:
                        content_to_check += record['answer'] + " "
                    if 'title' in record:
                        content_to_check += record['title'] + " "
                    if 'summary' in record:
                        content_to_check += record['summary'] + " "
                    
                    # 如果没找到预期字段，检查整个记录的字符串表示
                    if not content_to_check:
                        content_to_check = json.dumps(record, ensure_ascii=False)
                else:
                    content_to_check = json.dumps(record, ensure_ascii=False)
                
                # 应用筛选逻辑
                if should_keep(content_to_check):
                    out_f.write(line)
                    kept_records += 1
                
            except json.JSONDecodeError:
                print(f"警告: 跳过无效的JSON行: {line[:50]}...")
                continue
    
    return total_records, kept_records

def main():
    parser = argparse.ArgumentParser(description='筛选DevOps JSONL数据集中的日志管理和根因定位相关内容')
    parser.add_argument('--input', '-i', type=str, required=True, 
                        help='输入JSONL文件路径')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='输出JSONL文件路径')
    args = parser.parse_args()
    
    print(f"正在处理文件: {args.input}")
    total, kept = process_jsonl_file(args.input, args.output)
    
    print(f"处理完成:")
    print(f"- 总记录数: {total}")
    print(f"- 保留记录数: {kept}")
    print(f"- 保留比例: {kept/total*100:.2f}%")
    print(f"筛选后的数据已保存至: {args.output}")

if __name__ == "__main__":
    main()