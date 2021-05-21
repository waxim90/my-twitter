from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def test_comments(self):
        user = self.create_user('waxim')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        # print(comment.__str__())
        self.assertNotEqual(comment.__str__(), None)
