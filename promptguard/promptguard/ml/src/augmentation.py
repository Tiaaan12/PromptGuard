import pandas as pd
from augmentation_data import V1_injection, V1_benign


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

def save_augmentation(df, path):
    df.to_csv(path, index=False)