import os
import json
import app.modules.jieba_tw as jieba_tw
import app.modules.logger.logging as log
from config import BASE_DIR, LOG_DIR
import fnmatch
from app.modules.domain_chatbot.user import User
from gensim.models import word2vec


class Matcher():
    def __init__(self):
        try:
            # set jieba dict
            jieba_tw.set_dictionary(os.path.join(BASE_DIR, 'domain_matcher/jieba_dict/mydict.txt'))

            # set stopwords
            self.stopword_set = set()
            with open(os.path.join(BASE_DIR, 'domain_matcher/jieba_dict/stopwords.txt'),'r', encoding='utf-8') as stopwords:
                for stopword in stopwords:
                    self.stopword_set.add(stopword.strip('\n'))
            print('init Matcher')
        except:
            print('init error')
        
    def load_word2vec_model(self, MODEL_PATH):
        try:
            self.model = word2vec.Word2Vec.load(MODEL_PATH)
        except:
            print('load word2vec model error :(')
        
    def load_rule_data(self, RULE_DIR):
        file_data = []
        
        for filename in os.listdir(RULE_DIR):
            print("Loading: %s" % filename)

            with open(os.path.join(RULE_DIR, filename), 'r', encoding = 'UTF-8') as f:
                data = json.load(f)
                file_data.append(data)

        self.rule_data = file_data
        
    def filter_stopwords(self, sentence):
        newsen = '' # 去除停用詞後的句子
        jieba_tw.load_userdict(os.path.join(BASE_DIR, 'domain_matcher/custom/custom_key_words.txt'))
        words = jieba_tw.cut(sentence, cut_all=False)

        for word in words:
            if word not in self.stopword_set:
                newsen += word

        return newsen

    # flag => 主要功能為判斷是否為專用語設定
    # nickname => 區別目前使用者是否有設定專用語
    def match_domain(self, sentence, flag=None, user_nickname=None):
        # 在未斷詞前先取得句子，之後上傳對話紀錄到資料庫用
        User.get_question(sentence, user_nickname)

        # 個人化專屬語不需經過斷詞，且domain='none'
        if flag == 'user_nickname':
            jieba_tw.add_word(sentence, freq=200000)
            key_words = jieba_tw.cut(sentence, cut_all=False)
            key_words = list(key_words)
            print('key_words: %s' % key_words)
        else:
            newsen = self.filter_stopwords(sentence)
            key_words = jieba_tw.cut(newsen, cut_all=False)
            key_words = list(key_words)
            print('key_words: %s' % key_words)
        
        domain_score = self.match_domain_alg(key_words)

        return domain_score
    
    def match_domain_alg(self, key_words):
        logger = log.Logging('domain_match')
        logger.run(LOG_DIR)

        domain_score = []

        for word in key_words:
            try:
                float(word)
                dic = {'word': word, 'domain': '數字', 'result': []}
                domain_score.append(dic)
            except:
                exist_case = False
                err_message = ''

                dic = {'word': word, 'domain': '', 'result': []}
                threshold = 0.5
                # 180712, 判斷最大機率的domain
                max_score = 0
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

                            log_msg = 'similarity: %f, word: %s, concept: %s, score: %f, concept_count: %d' % (
                                self.model.similarity(word, concept), word, concept, score, concept_count)
                            logger.debug_msg(log_msg)
                            print('-----------')
                            print('similarity:', self.model.similarity(word, concept))
                            print('word:', word)
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
                        # 180712
                        if avg_score > max_score:
                            max_score = avg_score

                    dic['result'].append({domain: avg_score})
                    # 180712, 只加入最大的預測score
                    if avg_score>threshold and avg_score==max_score:
                        predict_domain = domain
                        dic['domain'] = predict_domain

                        success_msg = 'result => word: %s, avg_score: %f, this_domain: %s, predict_domain: %s' % (
                            word, avg_score, domain, predict_domain)
                        logger.debug_msg(success_msg)
                        print(success_msg)
                    else:
                        print('-----------')
                        dic['domain'] = predict_domain
                        fail_msg = 'result => word: %s, avg_score: %f, this_domain: %s, predict_domain: %s' % (
                            word, avg_score, domain, predict_domain)
                        logger.debug_msg(fail_msg)
                        print(fail_msg)

                if exist_case:
                    predict_domain = self.match_custom_key_words(word)
                    if predict_domain is not None:
                        dic['domain'] = predict_domain
                    else:
                        logger.error_msg(err_message)
                        print('-----------')
                        print(err_message)

                domain_score.append(dic)

        return domain_score

    def match_custom_key_words(self, word):
        print(word, '進行custom比對')
        file_data = []
        for filename in os.listdir(os.path.join(BASE_DIR, 'domain_matcher/custom')):
            if fnmatch.fnmatch(filename, '*.json'):
                with open(os.path.join(BASE_DIR, 'domain_matcher/custom/' + filename), 'r', encoding='UTF-8') as f:
                    data = json.load(f)
                    file_data.append(data)

        for rule in file_data:
            domain = rule['domain']
            for concept in rule['concepts']:
                if word == concept:
                    return domain
        return None