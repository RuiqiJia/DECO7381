
import django

from ...models import User
import operator

# load it when friend_list method in view.py finished editing
# from models import friend_list

"""
    Make recommendation based on the given user
    Four available spots will be used to show the recommended four users
    Recommendation criteria:
    Spot 1 -- not same country, same major
    Spot 2 -- not same country, the highest course similarity (Jaccard index)
    Spot 3 -- not same country, the highest topic similarity (Jaccard index)
    Spot 4 -- not same country, the highest all attribute similarity (Jaccard index)
"""


class MakeRecommendation:

    def __init__(self, user_id, user_name, topics, major, course, country):
        self.id = user_id
        self.name = user_name
        self.topics = topics
        self.major = major
        self.courses = course
        self.country = country

        # current user's attribute set
        self.country_list = [self.country]
        self.major_list = [self.major]
        self.topic_list = self.split_string(self.topics)
        self.course_list = self.split_string(self.courses)


    def jaccard_index_similarity(self, list1: list, list2: list) -> float:
        """
        Basic algorithm to calculate similarity
        list1: current user's unique attribute set
        list2: unique attribute set of user we indent to compare
        """
        s1 = set(list1)
        s2 = set(list2)

        return float(len(s1.intersection(s2)) / len(s1.union(s2)))

    def spot1_recommend(self):
        """
        Spot 1 recommend user with different nationality and then choose one with same major
        """
        # retrieve the first user object
        top_user = User.objects.exclude(Country=self.country).filter(Major=self.major)[:1].get()

        return top_user

    def spot2_recommend(self, eUser):
        """
        Spot 2 recommend user with different nationality and then calculate
        similarity based on course they enroll
        """

        similarity_score = dict()
        # step 1: filter user with different country
        queryset = User.objects.exclude(Country=self.country)
        total = queryset.count()

        # step 2: loop through each user to split their course list

        for user in queryset:
            compared = [user.Country]
            list1 = self.split_string(user.Courses)
            compared += list1
            similarity_score[user] = self.jaccard_index_similarity(self.country_list+self.course_list, compared)

        sorted_score = dict(sorted(similarity_score.items(), key=operator.itemgetter(1), reverse=True))

        uList = list(sorted_score.items())
        res = uList[0]

        if res[0] == eUser:
            res = uList[1]
        return res[0]


    def spot3_recommend(self, eUser1, eUser2):
        """
        Spot 3 recommend user with different nationality and then
        calculate similarity in topic selection
        """

        similarity_score = dict()
        # step 1: filter user with different country
        queryset = User.objects.exclude(Country=self.country)
        total = queryset.count()

        # step 2: loop through each user to split their course list

        for user in queryset:
            compared = [user.Country]
            list1 = self.split_string(user.Topics)

            compared = compared + list1
            similarity_score[user] = self.jaccard_index_similarity(self.country_list+self.topic_list, compared)

        sorted_score = dict(sorted(similarity_score.items(), key=operator.itemgetter(1), reverse=True))

        uList = list(sorted_score.items())
        res = uList[0]

        for i in range(len(uList)):
            if uList[i][0] not in [eUser1, eUser2]:
                return uList[i][0]



    def spot4_recommend(self, eUser1, eUser2, eUser3):
        """
        Spot 4 recommend user with different nationality and then calculate similarity
        based on all important attributes
        """
        similarity_score = dict()
        # step 1: filter user with different country
        queryset = User.objects.exclude(Country=self.country)
        total = queryset.count()

        # step 2: loop through each user to split their course list

        for user in queryset:
            compared = [user.Country, user.Major]
            list1 = self.split_string(user.Topics)
            list2 = self.split_string(user.Courses)
            compared = compared + list1 + list2
            similarity_score[user] = self.jaccard_index_similarity(self.major_list+self.topic_list+self.course_list+self.country_list, compared)

        sorted_score = dict(sorted(similarity_score.items(), key=operator.itemgetter(1), reverse=True))

        uList = list(sorted_score.items())


        for i in range(len(uList)):
            if uList[i][0] not in [eUser1, eUser2, eUser3]:
                return uList[i][0]



    def split_string(self, string_sequence: str) -> list:
        """
        Helper method to split topic/course
        topics: input topic string
        Return:
            list contains all topic
        """

        string_list = []
        # return empty list if it is empty
        if string_sequence is None:
            return string_list
        # split the string and strip the whitespace
        else:
            string_list = string_sequence.split(",")

            for i in range(len(string_list)):
                string_list[i] = string_list[i].strip()
        return string_list


def main():
    print("Hello World!")


if __name__ == "__main__":
    main()
