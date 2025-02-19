"""
Views handling read (GET) requests for the Discussion tab and inline discussions.
"""


from django.conf import settings
from django.utils.translation import gettext_noop

import lms.djangoapps.discussion.django_comment_client.utils as utils
from lms.djangoapps.courseware.tabs import EnrolledTab
from lms.djangoapps.discussion.toggles import ENABLE_DISCUSSIONS_MFE
from openedx.core.djangoapps.discussions.url_helpers import get_discussions_mfe_url
from openedx.features.lti_course_tab.tab import DiscussionLtiCourseTab
from xmodule.tabs import TabFragmentViewMixin


class DiscussionTab(TabFragmentViewMixin, EnrolledTab):
    """
    A tab for the cs_comments_service forums.
    """

    type = 'discussion'
    title = gettext_noop('Discussion')
    priority = 40
    view_name = 'forum_form_discussion'
    fragment_view_name = 'lms.djangoapps.discussion.views.DiscussionBoardFragmentView'
    is_hideable = settings.FEATURES.get('ALLOW_HIDING_DISCUSSION_TAB', False)
    is_default = False
    body_class = 'discussion'
    online_help_token = 'discussions'

    @property
    def link_func(self):
        """ Returns a function that returns the course tab's URL. """
        _link_func = super().link_func

        def link_func(course, reverse_func):
            """ Returns a function that returns the course tab's URL. """
            mfe_url = get_discussions_mfe_url(course.id)
            if ENABLE_DISCUSSIONS_MFE.is_enabled(course.id) and mfe_url:
                return mfe_url
            return _link_func(course, reverse_func)

        return link_func

    @classmethod
    def is_enabled(cls, course, user=None):
        if not super().is_enabled(course, user):
            return False
        # Disable the regular discussion tab if LTI-based external Discussion forum is enabled
        if DiscussionLtiCourseTab.is_enabled(course, user):
            return False
        return utils.is_discussion_enabled(course.id)
