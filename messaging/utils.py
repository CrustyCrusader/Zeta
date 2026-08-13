from accounts.models import Follow


def is_mutual_follow(user_a, user_b):
    if user_a == user_b:
        return False

    return (
        Follow.objects.filter(follower=user_a, following=user_b).exists()
        and Follow.objects.filter(follower=user_b, following=user_a).exists()
    )