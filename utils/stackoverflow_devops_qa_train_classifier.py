import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
import os

# Define file paths
BASE_PATH = "/Users/rizhiyi/Downloads/logsllm_datasets/data/sft/运维通用问答/"
LOG_RELATED_FILE = os.path.join(BASE_PATH, "Devops_Stackoverflow_summarization_log_related_filtered.jsonl")
CI_CD_FILE = os.path.join(BASE_PATH, "Devops_Stackoverflow_summarization_cicd_related.jsonl")
DATA_TO_CLASSIFY_FILE = os.path.join(BASE_PATH, "Devops_Stackoverflow_summarization_deduplicated.jsonl")
OUTPUT_FILE = os.path.join(BASE_PATH, "Devops_Stackoverflow_summarization_classified.jsonl")

# Load a pre-trained sentence transformer model
# Using a multilingual model as the data might contain mixed language or technical terms
# For purely Chinese text, a Chinese-specific model might be more performant
# For English, models like 'all-MiniLM-L6-v2' are common
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
print(f"Loading sentence transformer model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("Sentence transformer model loaded.")

def load_jsonl(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {file_path}: {e}")
        return []
    return data

def save_jsonl(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def get_texts_from_data(dataset):
    texts = []
    for item in dataset:
        # Assuming the relevant text is in 'prompt' or 'question' or 'answer'
        # Prioritize 'prompt', then 'question', then 'answer'
        text_content = item.get('prompt', item.get('question', item.get('answer', '')))
        if isinstance(text_content, str) and text_content.strip():
            texts.append(text_content.strip())
        else:
            # Handle cases where text might be missing or not a string
            # For now, we'll append an empty string, but this might need better handling
            texts.append('') 
    return texts

print("Starting data loading and preprocessing...")

# 1. Load training data
log_data = load_jsonl(LOG_RELATED_FILE)
cicd_data = load_jsonl(CI_CD_FILE)

if not log_data:
    print(f"No data loaded from {LOG_RELATED_FILE}. Cannot proceed with training.")
    exit()
if not cicd_data:
    print(f"No data loaded from {CI_CD_FILE}. Cannot proceed with training.")
    exit()

print(f"Loaded {len(log_data)} log-related items and {len(cicd_data)} CI/CD-related items.")

# Prepare training texts and labels
# Label: 1 for '日志/可观测性', 0 for 'CI/CD/通用编程'
log_texts = get_texts_from_data(log_data)
cicd_texts = get_texts_from_data(cicd_data)

# Filter out empty texts that might have resulted from get_texts_from_data
log_texts_filtered = [text for text in log_texts if text]
cicd_texts_filtered = [text for text in cicd_texts if text]

if not log_texts_filtered:
    print("No valid text found in log-related data after filtering. Cannot train.")
    exit()
if not cicd_texts_filtered:
    print("No valid text found in CI/CD-related data after filtering. Cannot train.")
    exit()

train_texts = log_texts_filtered + cicd_texts_filtered
labels = np.array([1] * len(log_texts_filtered) + [0] * len(cicd_texts_filtered))

print(f"Total training samples: {len(train_texts)}")

# 2. Generate embeddings for training data
print("Generating embeddings for training data...")
train_embeddings = model.encode(train_texts, show_progress_bar=True)
print("Training embeddings generated.")

# 3. Train a classifier (Logistic Regression)
print("Training the classifier...")
classifier = LogisticRegression(solver='liblinear', random_state=42)
classifier.fit(train_embeddings, labels)
print("Classifier training complete.")

# 4. Load data to be classified
print(f"Loading data to classify from {DATA_TO_CLASSIFY_FILE}...")
data_to_classify = load_jsonl(DATA_TO_CLASSIFY_FILE)

if not data_to_classify:
    print(f"No data loaded from {DATA_TO_CLASSIFY_FILE}. Classification step will be skipped.")
else:
    print(f"Loaded {len(data_to_classify)} items to classify.")
    classify_texts_raw = get_texts_from_data(data_to_classify)
    
    # We need to keep track of original items even if their text is empty for classification
    # So, we'll generate embeddings for non-empty texts and assign a default prediction for empty ones.
    
    valid_texts_for_classification = []
    original_indices_for_valid_texts = []
    
    for i, text in enumerate(classify_texts_raw):
        if text:
            valid_texts_for_classification.append(text)
            original_indices_for_valid_texts.append(i)
            
    if not valid_texts_for_classification:
        print("No valid text found in the data to classify. All items will be marked with a default prediction or skipped.")
        # Assign a default label or handle as per requirements
        for item in data_to_classify:
            item['predicted_category'] = 'unknown_due_to_empty_text'
    else:
        print(f"Generating embeddings for {len(valid_texts_for_classification)} non-empty items to classify...")
        classify_embeddings = model.encode(valid_texts_for_classification, show_progress_bar=True)
        print("Classification embeddings generated.")

        # 5. Predict labels for the data
        print("Predicting categories...")
        predictions = classifier.predict(classify_embeddings)
        probabilities = classifier.predict_proba(classify_embeddings)
        print("Prediction complete.")

        # Assign predictions back to the original data structure
        # Initialize with a default prediction for all items
        all_predictions = ['unknown_prediction'] * len(data_to_classify)
        all_probabilities_log = [0.0] * len(data_to_classify)
        all_probabilities_cicd = [0.0] * len(data_to_classify)

        for i, original_idx in enumerate(original_indices_for_valid_texts):
            predicted_label = predictions[i]
            all_predictions[original_idx] = '日志/可观测性' if predicted_label == 1 else 'CI/CD/通用编程'
            # probabilities are [P(class_0), P(class_1)]
            all_probabilities_cicd[original_idx] = probabilities[i][0] # Assuming 0 is CI/CD
            all_probabilities_log[original_idx] = probabilities[i][1]  # Assuming 1 is Log

        for i, item in enumerate(data_to_classify):
            item['predicted_category'] = all_predictions[i]
            item['prediction_probability_log'] = all_probabilities_log[i]
            item['prediction_probability_cicd'] = all_probabilities_cicd[i]
            if all_predictions[i] == 'unknown_prediction' and not classify_texts_raw[i]: # If it was an empty text initially
                 item['predicted_category'] = 'unknown_due_to_empty_text'

    # 6. Save the classified data
    print(f"Saving classified data to {OUTPUT_FILE}...")
    save_jsonl(OUTPUT_FILE, data_to_classify)
    print(f"Classification complete. Results saved to {OUTPUT_FILE}")

print("Script finished.")