from models import User


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
        top_user = User.objects.exclude(Country=self.country).filter(Major=self.major)[:1]

        return top_user

    def spot2_recommend(self):
        """
        Spot 2 recommend user with different nationality and then calculate
        similarity based on course they enroll
        """
        # step 1: filter user with different country

        # step 2: loop through each user to split their course list

        # step 3: calculate each individual similarity score

        # step 4: descending order the similarity score and get the user



    def spot3_recommend(self):
        """
        Spot 3 recommend user with different nationality and then
        calculate similarity in topic selection
        """
        # step 1: filter user with different country

        # step 2: loop through each user to split their topic list

        # step 3: calculate each individual similarity score

        # step 4: descending order the similarity score and get the top user



    def spot4_recommend(self):
        """
        Spot 4 recommend user with different nationality and then calculate similarity
        based on all important attributes
        """






    def split_string(self, topics: str) -> list:
        """
        Helper method to split topic/course
        topics: input topic string
        Return:
            list contains all topic
        """


