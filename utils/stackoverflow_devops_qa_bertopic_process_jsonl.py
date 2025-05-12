import json
from bertopic import BERTopic
import pandas as pd

def load_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def save_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    input_file = '/Users/rizhiyi/Downloads/logsllm_datasets/data/sft/运维通用问答/Devops_Stackoverflow_summarization_log_related.jsonl'
    output_file = '/Users/rizhiyi/Downloads/logsllm_datasets/data/sft/运维通用问答/Devops_Stackoverflow_summarization_log_related_filtered.jsonl'

    print(f"Loading data from {input_file}...")
    dataset = load_data(input_file)
    
    if not dataset:
        print("No data loaded. Exiting.")
        return

    # Extract prompts for topic modeling
    # Assuming the relevant text is in the 'prompt' field
    documents = [item['prompt'] for item in dataset if 'prompt' in item]
    
    if not documents:
        print("No documents found for topic modeling. Exiting.")
        return

    print(f"Found {len(documents)} documents for topic modeling.")

    # Initialize BERTopic model
    # Using a pre-trained sentence transformer model suitable for multilingual or general text
    # For Chinese text, consider models like 'paraphrase-multilingual-MiniLM-L12-v2' or specific Chinese models
    # For faster processing, especially for a potentially large dataset, we can reduce n_neighbors or min_topic_size
    print("Initializing BERTopic model...")
    topic_model = BERTopic(verbose=True, language="multilingual", min_topic_size=5, n_gram_range=(1,2))

    print("Fitting BERTopic model...")
    topics, probabilities = topic_model.fit_transform(documents)

    print("Topic modeling complete.")
    topic_info_df = topic_model.get_topic_info()
    print("Topic Info:")
    print(topic_info_df)

    # Define keywords for '日志/可观测性'
    # These keywords should be in the language of the documents or reflect concepts
    log_observability_keywords = [
        'log', 'logging', 'logs', '日志', 
        'monitor', 'monitoring', '监控',
        'observability', '可观测性', 
        'trace', 'tracing', '追踪',
        'metric', 'metrics', '指标',
        'elk', 'elasticsearch', 'logstash', 'kibana',
        'prometheus', 'grafana', 
        'xdebug', 'gelf', 'syslog', 
        'cloud logs viewer', 'cloud run', 'docker', 'container',
        'perf_event_paranoid', 'audit', 'alert', 'event'
    ]

    relevant_topic_ids = set()
    for index, row in topic_info_df.iterrows():
        # Topic -1 is for outliers, skip it
        if row['Topic'] == -1:
            continue
        # Check if any keyword is in the topic name/representation
        # The 'Name' column usually contains representative words for the topic
        topic_words = row['Name'].lower().split('_') + [word.lower() for word_tuple in topic_model.get_topic(row['Topic']) for word in word_tuple if isinstance(word, str)]
        
        for kw in log_observability_keywords:
            if kw.lower() in topic_words:
                relevant_topic_ids.add(row['Topic'])
                print(f"Topic {row['Topic']} ('{row['Name']}') identified as relevant due to keyword: {kw}")
                break
    
    if not relevant_topic_ids:
        print("No topics related to '日志/可观测性' were automatically identified. Please inspect topics manually or adjust keywords.")
        # As a fallback, you might want to include all data or a subset based on other criteria, or stop
        # For now, we'll output an empty file if no relevant topics are found.
        filtered_data = []
    else:
        print(f"Identified relevant topic IDs: {relevant_topic_ids}")
        
        # Filter original dataset
        # Ensure 'topics' list aligns with 'documents' list, which aligns with 'dataset' if all items had prompts
        # Need to map topics back to original dataset items carefully
        
        # Create a mapping from document index to original dataset index
        doc_to_original_idx = []
        for i, item in enumerate(dataset):
            if 'prompt' in item:
                doc_to_original_idx.append(i)

        filtered_data = []
        for i, topic_id in enumerate(topics):
            if topic_id in relevant_topic_ids:
                original_idx = doc_to_original_idx[i]
                filtered_data.append(dataset[original_idx])

    print(f"Filtered down to {len(filtered_data)} items.")
    save_data(output_file, filtered_data)
    print(f"Filtered data saved to {output_file}")

if __name__ == '__main__':
    main()