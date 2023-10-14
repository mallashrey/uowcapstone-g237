from tqdm import tqdm

MAX_LEN = 512

def tokenize_sentences(sentences, tokenizer, max_seq_len = MAX_LEN):
    tokenized_sentences = []
    truncation_strategy = 'only_first'

    for sentence in tqdm(sentences):
        tokenized_sentence = tokenizer.encode(
                            sentence,                  # Sentence to encode.
                            add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                            max_length = max_seq_len,  # Truncate all sentences.
                            truncation=truncation_strategy
                    )

        tokenized_sentences.append(tokenized_sentence)

    return tokenized_sentences