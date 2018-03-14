import os
from config import BASE_DIR, LOG_DIR
import json
import jieba.analyse
import app.modules.logger.logging as log
import fnmatch
from gensim.models import word2vec
import codecs

# init data
# self.model: word2vec model
# self.rule_data

class Matcher(object):
    def __init__(self):
        print('init Matcher')
        
    def load_word2vec_model(self, MODEL_PATH):
        try:
            self.model = word2vec.Word2Vec.load(MODEL_PATH)
            print('loading model complete :)')
        except err:
            print(err)
            print('load word2vec model error :(')
        
    def load_rule_data(self, RULE_DIR):
        file_data = []
        
        for filename in os.listdir(RULE_DIR):
            print("Loading: %s" % filename)
            
            with open(os.path.join(RULE_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_data.append(data)

        self.rule_data = file_data

    def match_domain(self, sentence):
        logger = log.Logging('test')
        logger.run(os.path.join(LOG_DIR, 'domain_match.log'))
        jieba.load_userdict(os.path.join(BASE_DIR, 'domain_matcher/custom/custom_key_words.txt'))
        
        key_words = jieba.analyse.extract_tags(sentence, topK = 20, withWeight = False, allowPOS=())
        print('key_words: %s' % key_words)
        
        domain_score = []

        for index, word in enumerate(key_words):
            exist_case = False
            err_message = ''

            dic = {'word': word, 'domain': '', 'result': []}
            threshold = 0.3
            predict_domain = 'none'
    
            for rule in self.rule_data:
                domain = rule['domain']
                score = 0
                concept_count = 0
        
                for concept in rule['concepts']:
                    try:
                        similarity = self.model.similarity(word, concept)
                        score += similarity
                        concept_count += 1

                        log_msg = 'similarity: %f, word: %s, concept: %s, score: %f, concept_count: %d' % (self.model.similarity(word, concept), word, concept, score, concept_count)
                        logger.debug_msg(log_msg)
                        print('-----------')
                        print('similarity:', self.model.similarity(word, concept))
                        print('word:',  word)
                        print('concept:', concept)
                        print('concept_count:', concept_count)
                
                    except KeyError as err:
                        exist_case = True
                        err_message = err
                        break

                if concept_count == 0:
                    avg_score = 0
                else:
                    avg_score = score / concept_count
                    
                dic['result'].append({domain: avg_score})
                if avg_score > threshold:
                    predict_domain = domain
                    dic['domain'] = predict_domain
                    
                    success_msg = 'result => word: %s, avg_score: %f, this_domain: %s, predict_domain: %s' % (word, avg_score, domain, predict_domain)
                    logger.debug_msg(success_msg)
                    print(success_msg)
                else:
                    # predict_domain = 'none'
                    dic['domain'] = predict_domain
                    fail_msg = 'result => word: %s, avg_score: %f, this_domain: %s, predict_domain: %s' % (word, avg_score, domain, predict_domain)
                    logger.debug_msg(fail_msg)
                    print(fail_msg)

            if exist_case:
                predict_domain = self.match_custom_key_words(word)
                if predict_domain is not None:
                    dic['domain'] = predict_domain
                else:
                    logger.error_msg(err_message)
                    print(err_message)

            domain_score.append(dic)
        return domain_score

    def match_custom_key_words(self, word):
        file_data = []
        for filename in os.listdir(os.path.join(os.getcwd(), 'app/modules/domain_matcher/custom')):
            if fnmatch.fnmatch(filename, '*.json'):
                with open(os.path.join(os.getcwd(), 'app/modules/domain_matcher/custom/' + filename), 'r', encoding='UTF-8') as f:
                    data = json.load(f)
                    file_data.append(data)

        for rule in file_data:
            domain = rule['domain']
            for concept in rule['concepts']:
                if word == concept:
                    return domain
        return None