from .models import Learner  # Adjust the import path as needed

def update_learner_usernames():
    learners = Learner.objects.all()
    for learner in learners:
        learner.learner_username = learner.user.username
        learner.save()

if __name__ == '__main__':
    update_learner_usernames()