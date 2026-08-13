from django import forms

from accounts.models import Follow, User

from .utils import is_mutual_follow


class GroupCreateForm(forms.Form):
    name = forms.CharField(max_length=120)
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            following_ids = Follow.objects.filter(
                follower=user
            ).values_list("following_id", flat=True)

            follower_ids = Follow.objects.filter(
                following=user
            ).values_list("follower_id", flat=True)

            mutual_ids = set(following_ids) & set(follower_ids)

            self.fields["participants"].queryset = User.objects.filter(
                id__in=mutual_ids
            )