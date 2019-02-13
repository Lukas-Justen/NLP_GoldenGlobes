import copy
import re


class TweetCategorizer:

    def __init__(self, group_indicators, stopwords, group_name, tweets, threshold, sample_size):
        group_indicators = sorted(group_indicators, key=len)
        self.tweets = tweets.sample(frac=1)[:sample_size]
        self.stripper = re.compile(r'\b(\w+)-(\w+)\b')
        self.entity_finder = re.compile(r'(?P<entity>([A-Z][A-Za-z]*\s?)+\b(?<=[a-zA-Z]))')
        self.people_finder = re.compile(r'actor|actress|director|singer|songwriter|composer|regisseur|cecil|host|entertain|moderat')
        self.detecter = []
        self.replacor = []
        self.threshold = threshold
        self.winners = {}
        self.group_name = group_name
        self.original_groups = copy.deepcopy(group_indicators)
        self.group_indicators = self.strip_indicators(group_indicators, stopwords)
        self.tweets = self.apply_indicators(self.group_indicators, group_name, self.tweets)

    def strip_indicators(self, group_indicators, stopwords):
        for index in range(0, len(group_indicators)):
            text = str(group_indicators[index]).lower()
            text = " ".join("" if x in stopwords else x for x in text.split())
            matches = self.stripper.findall(text)
            for match in matches:
                text = text + " " + str(match[0]) + str(match[1])
            group_indicators[index] = "|".join(text.split())
            self.detecter.append(re.compile(str(group_indicators[index])))
            self.replacor.append(re.compile(str(group_indicators[index]), flags=re.IGNORECASE))
        return group_indicators

    def apply_indicators(self, group_indicators, group_name, tweets):
        tweets[group_name] = tweets["clean_upper"].apply(lambda text: self.detect_group(text, group_indicators))
        return tweets

    def detect_group(self, text, group_indicators):
        counts_per_group = dict.fromkeys(range(0, len(group_indicators)), 0)
        text = str(text).lower()
        for index in range(0, len(group_indicators)):
            matches = self.detecter[index].findall(text)
            counts_per_group[index] = len(matches)
        max_value = max(counts_per_group.values())
        return max(counts_per_group, key=counts_per_group.get) if max_value > self.threshold else -1

    def get_categorized_tweets(self):
        categorized_tweets = self.tweets[self.tweets[self.group_name] > -1]
        # categorized_tweets = categorized_tweets.sort_values(by=[self.group_name, "hour", "minute"])
        return categorized_tweets

    def count_entity(self, text, entity_count, category):
        text = self.replacor[category].sub(' ', text)
        matches = self.entity_finder.findall(text)
        entity_count = self.aggregate_entity_count(matches, entity_count)
        return entity_count

    def aggregate_entity_count(self, matches, entity_count):
        for match in matches:
            for m in match:
                entity_count[m] = 1 if m not in entity_count.keys() else entity_count[m] + 1
        return entity_count

    def find_list_of_entities(self, tweets, number_entities, verification_people, verification_things):
        self.winners = {}
        for i in range(0, len(self.group_indicators)):
            associated_tweets = tweets[tweets[self.group_name] == i]
            entities = self.count_entities(associated_tweets, i)
            if self.people_finder.findall(self.original_groups[i]):
                entities = {key: entities[key] for key in entities if key in verification_people}
            else:
                entities = {key: entities[key] for key in entities if key in verification_things}
            entities = sorted(entities, key=entities.get, reverse=True)
            actual_found = number_entities if number_entities < len(entities) else len(entities)
            if actual_found == 1:
                self.winners[self.original_groups[i]] = str(entities[0]).lower()
            else:
                self.winners[self.original_groups[i]] = [str(entities[j]).lower() for j in range(0, actual_found)]
        return self.winners

    def count_entities(self, tweets, group_index):
        entities = {}
        for index, row in tweets.iterrows():
            entities = self.count_entity(row['clean_upper'], entities, group_index)
        return entities

    def print_frequent_entities(self):
        for key in sorted(self.winners):
            print("Entity: ", self.winners[key], "Group: ", key)
