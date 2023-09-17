#embedding
import torch
import torch.nn as nn

vocab_size = 40000
embedding_dim = 8

embedding_layer = nn.Embedding(vocab_size, embedding_dim)

# 加载保存的模型参数到新的嵌入层
embedding_layer.load_state_dict(torch.load('my_embedding_layer.pth'))

#tokenizer
from transformers import AutoTokenizer
my_tokenizer = AutoTokenizer.from_pretrained('my_tokenizer')
 
import joblib
# 加载KMeans模型
loaded_kmeans = joblib.load('clustering_model.pkl')

import torch
import torch.nn as nn

class DataPreprocessingModel(nn.Module):
    def __init__(self, tokenizer, embedding_layer, max_sequence_length):
        super(DataPreprocessingModel, self).__init__()
        self.tokenizer = tokenizer
        self.embedding_layer = embedding_layer
        self.max_sequence_length = max_sequence_length

    def forward(self, input_text):
        # Tokenize input text
        tokenized_text = self.tokenizer.tokenize(input_text)
        
        # Ensure the sequence length does not exceed max_sequence_length
        tokenized_text = tokenized_text[:self.max_sequence_length]
        
        # Convert tokens to IDs
        input_ids = self.tokenizer.convert_tokens_to_ids(tokenized_text)
        
        # Pad the sequence to max_sequence_length if necessary
        if len(input_ids) < self.max_sequence_length:
            input_ids += [0] * (self.max_sequence_length - len(input_ids))
        
        # Convert to tensor and apply embedding
        input_tensor = torch.tensor(input_ids)
        embedded_tensor = self.embedding_layer(input_tensor)
        
        # Reshape the embedded tensor to (3424,)
        embedded_tensor = embedded_tensor.reshape(3424)

        return embedded_tensor
    
# Usage
max_sequence_length = 428  # max sequence length
preprocessing_model = DataPreprocessingModel(my_tokenizer, embedding_layer, max_sequence_length)

def preprocess_text(input_text):
    tokenized_text = my_tokenizer.tokenize(input_text)
    tokenized_text = tokenized_text[:max_sequence_length]
    input_ids = my_tokenizer.convert_tokens_to_ids(tokenized_text)

    if len(input_ids) < max_sequence_length:
        input_ids += [0] * (max_sequence_length - len(input_ids))

    input_tensor = torch.tensor(input_ids)
    embedded_tensor = embedding_layer(input_tensor)
    embedded_tensor = embedded_tensor.reshape(3424)

    return embedded_tensor

def predict_cluster(input_text):
    preprocessed_data = preprocess_text(input_text)
    predicted_labels = loaded_kmeans.predict(preprocessed_data.detach().numpy().reshape(1, -1).astype('float'))
    return predicted_labels[0]
