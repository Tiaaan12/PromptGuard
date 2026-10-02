import pandas as pd
from augmentation_data import V1_injection, V1_benign, V2_injection, V2_benign, V3_injection, V3_benign


def create_augmentation_v1():
    
    synthetic_texts = (
        V1_injection["code_injections"]
        + V1_injection["indirect_extraction"]
        + V1_injection["paraphrased_injections"]
        + V1_benign["benign_security_discussion"]
        + V1_benign["benign_code_discussion"]

    )

    synthetic_labels = (
        [1] * len(V1_injection["code_injections"])
        + [1] * len(V1_injection["indirect_extraction"])
        + [1] * len(V1_injection["paraphrased_injections"])
        + [0] * len(V1_benign["benign_security_discussion"])
        + [0] * len(V1_benign["benign_code_discussion"])
    )

    return pd.DataFrame({
        "text" : synthetic_texts,
        "target" : synthetic_labels  
    })


def create_augmentation_v2():
    
    synthetic_texts = (
        V1_injection["code_injections"]
        + V1_injection["indirect_extraction"]
        + V1_injection["paraphrased_injections"]
        + V2_injection["indirect_semantic_extraction"]
        + V1_benign["benign_security_discussion"]
        + V1_benign["benign_code_discussion"]
        + V2_benign["benign_instruction_discussion"]

    )

    synthetic_labels = (
        [1] * len(V1_injection["code_injections"])
        + [1] * len(V1_injection["indirect_extraction"])
        + [1] * len(V1_injection["paraphrased_injections"])
        + [1] * len(V2_injection["indirect_semantic_extraction"])
        + [0] * len(V1_benign["benign_security_discussion"])
        + [0] * len(V1_benign["benign_code_discussion"])
        + [0] * len(V2_benign["benign_instruction_discussion"])
    )

    return pd.DataFrame({
        "text" : synthetic_texts,
        "target" : synthetic_labels  
    })

def create_augmentation_v3():
    
    synthetic_texts = (
        V1_injection["code_injections"]
        + V1_injection["indirect_extraction"]
        + V1_injection["paraphrased_injections"]
        + V2_injection["indirect_semantic_extraction"]
        + V1_benign["benign_security_discussion"]
        + V1_benign["benign_code_discussion"]
        + V2_benign["benign_instruction_discussion"]
        + V3_injection["obfuscated_injections"]
        + V3_injection["encoded_injections"]
        + V3_benign["benign_encoding_discussion"]
        + V3_benign["benign_encoded_examples"]

    )

    synthetic_labels = (
        [1] * len(V1_injection["code_injections"])
        + [1] * len(V1_injection["indirect_extraction"])
        + [1] * len(V1_injection["paraphrased_injections"])
        + [1] * len(V2_injection["indirect_semantic_extraction"])
        + [0] * len(V1_benign["benign_security_discussion"])
        + [0] * len(V1_benign["benign_code_discussion"])
        + [0] * len(V2_benign["benign_instruction_discussion"])
        + [1] * len(V3_injection["obfuscated_injections"])
        + [1] * len(V3_injection["encoded_injections"])
        + [0] * len(V3_benign["benign_encoding_discussion"])
        + [0] * len(V3_benign["benign_encoded_examples"])
    )

    return pd.DataFrame({
        "text" : synthetic_texts,
        "target" : synthetic_labels  
    })

def combine_training_data(X_train, y_train, augmented_df):
    pass
    

def save_augmentation(df, path):
    df.to_csv(path, index=False)