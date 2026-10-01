from Video.models import Video
from blog.models import Article
from comments.models import Comment
from products.models import Product


def hide_reported_object(target):
    if isinstance(target, Video):
        target.visibility = Video.Visibility.PRIVATE
        target.save(update_fields=["visibility"])
        return True
    if isinstance(target, Article):
        target.active = False
        target.save(update_fields=["active"])
        return True
    if isinstance(target, Product):
        target.is_hidden = True
        target.save(update_fields=["is_hidden"])
        return True
    if isinstance(target, Comment):
        target.is_hidden = True
        target.save(update_fields=["is_hidden"])
        return True
    return False