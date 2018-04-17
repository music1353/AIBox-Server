# Domain Matcher

* 基於jieba_tw斷詞及gensim word2vec model
* 將句子分類至不同的流程（疾病、地點、個人化...）



## Get Started

```python
from domain_matcher.matcher import Matcher

matcher = Matcher()

# init rule data and model
matcher.load_rule_data('domain_matcher/rule')
matcher.load_word2vec_model("training_model/20180320all_model.bin")
```



## Match Domain

```python
sentence = input('請輸入句子：')
domain_score = matcher.match_domain(sentence)
```

