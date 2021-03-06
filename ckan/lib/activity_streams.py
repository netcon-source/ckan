import re

from pylons.i18n import _
from webhelpers.html import literal

import ckan.lib.helpers as h
import ckan.lib.base as base
import ckan.logic as logic

# get_snippet_*() functions replace placeholders like {user}, {dataset}, etc.
# in activity strings with HTML representations of particular users, datasets,
# etc.

def get_snippet_actor(activity, detail):
    return literal('''<span class="actor" data-module="popover-context" data-module-type="user" data-module-id="%s">%s</span>'''
        % (activity['user_id'], h.linked_user(activity['user_id'], 0, 30))
        )

def get_snippet_user(activity, detail):
    return literal('''<span data-module="popover-context" data-module-type="user" data-module-id="%s">%s</span>'''
        % (activity['object_id'], h.linked_user(activity['object_id'], 0, 20))
        )

def get_snippet_dataset(activity, detail):
    data = activity['data']
    link = h.dataset_link(data.get('package') or data.get('dataset'))
    return literal('''<span data-module="popover-context" data-module-type="dataset" data-module-id="%s">%s</span>'''
        % (activity['object_id'], link)
        )

def get_snippet_tag(activity, detail):
    return h.tag_link(detail['data']['tag'])

def get_snippet_group(activity, detail):
    return h.group_link(activity['data']['group'])

def get_snippet_extra(activity, detail):
    return '"%s"' % detail['data']['package_extra']['key']

def get_snippet_resource(activity, detail):
    return h.resource_link(detail['data']['resource'],
                           activity['data']['package']['id'])

def get_snippet_related_item(activity, detail):
    return h.related_item_link(activity['data']['related'])

def get_snippet_related_type(activity, detail):
    # FIXME this needs to be translated
    return activity['data']['related']['type']

# activity_stream_string_*() functions return translatable string
# representations of activity types, the strings contain placeholders like
# {user}, {dataset} etc. to be replaced with snippets from the get_snippet_*()
# functions above.

def activity_stream_string_added_tag():
    return _("{actor} added the tag {tag} to the dataset {dataset}")

def activity_stream_string_changed_group():
    return _("{actor} updated the group {group}")

def activity_stream_string_changed_package():
    return _("{actor} updated the dataset {dataset}")

def activity_stream_string_changed_package_extra():
    return _("{actor} changed the extra {extra} of the dataset {dataset}")

def activity_stream_string_changed_resource():
    return _("{actor} updated the resource {resource} in the dataset {dataset}")

def activity_stream_string_changed_user():
    return _("{actor} updated their profile")

def activity_stream_string_deleted_group():
    return _("{actor} deleted the group {group}")

def activity_stream_string_deleted_package():
    return _("{actor} deleted the dataset {dataset}")

def activity_stream_string_deleted_package_extra():
    return _("{actor} deleted the extra {extra} from the dataset {dataset}")

def activity_stream_string_deleted_resource():
    return _("{actor} deleted the resource {resource} from the dataset {dataset}")

def activity_stream_string_new_group():
    return _("{actor} created the group {group}")

def activity_stream_string_new_package():
    return _("{actor} created the dataset {dataset}")

def activity_stream_string_new_package_extra():
    return _("{actor} added the extra {extra} to the dataset {dataset}")

def activity_stream_string_new_resource():
    return _("{actor} added the resource {resource} to the dataset {dataset}")

def activity_stream_string_new_user():
    return _("{actor} signed up")

def activity_stream_string_removed_tag():
    return _("{actor} removed the tag {tag} from the dataset {dataset}")

def activity_stream_string_deleted_related_item():
    return _("{actor} deleted the related item {related_item}")

def activity_stream_string_follow_dataset():
    return _("{actor} started following {dataset}")

def activity_stream_string_follow_user():
    return _("{actor} started following {user}")

def activity_stream_string_new_related_item():
    return _("{actor} created the link to related {related_type} {related_item}")

# A dictionary mapping activity snippets to functions that expand the snippets.
activity_snippet_functions = {
    'actor': get_snippet_actor,
    'user': get_snippet_user,
    'dataset': get_snippet_dataset,
    'tag': get_snippet_tag,
    'group': get_snippet_group,
    'extra': get_snippet_extra,
    'resource': get_snippet_resource,
    'related_item': get_snippet_related_item,
    'related_type': get_snippet_related_type,
}

# A dictionary mapping activity types to functions that return translatable
# string descriptions of the activity types.
activity_stream_string_functions = {
  'added tag': activity_stream_string_added_tag,
  'changed group': activity_stream_string_changed_group,
  'changed package': activity_stream_string_changed_package,
  'changed package_extra': activity_stream_string_changed_package_extra,
  'changed resource': activity_stream_string_changed_resource,
  'changed user': activity_stream_string_changed_user,
  'deleted group': activity_stream_string_deleted_group,
  'deleted package': activity_stream_string_deleted_package,
  'deleted package_extra': activity_stream_string_deleted_package_extra,
  'deleted resource': activity_stream_string_deleted_resource,
  'new group': activity_stream_string_new_group,
  'new package': activity_stream_string_new_package,
  'new package_extra': activity_stream_string_new_package_extra,
  'new resource': activity_stream_string_new_resource,
  'new user': activity_stream_string_new_user,
  'removed tag': activity_stream_string_removed_tag,
  'deleted related item': activity_stream_string_deleted_related_item,
  'follow dataset': activity_stream_string_follow_dataset,
  'follow user': activity_stream_string_follow_user,
  'new related item': activity_stream_string_new_related_item,
}

# A dictionary mapping activity types to the icons associated to them
activity_stream_string_icons = {
  'added tag': 'tag',
  'changed group': 'users',
  'changed package': 'sitemap',
  'changed package_extra': 'edit',
  'changed resource': 'file',
  'changed user': 'user',
  'deleted group': 'users',
  'deleted package': 'sitemap',
  'deleted package_extra': 'edit',
  'deleted resource': 'file',
  'new group': 'users',
  'new package': 'sitemap',
  'new package_extra': 'edit',
  'new resource': 'file',
  'new user': 'user',
  'removed tag': 'tag',
  'deleted related item': 'picture',
  'follow dataset': 'sitemap',
  'follow user': 'user',
  'new related item': 'picture',
}

# A list of activity types that may have details
activity_stream_actions_with_detail = ['changed package']

def activity_list_to_html(context, activity_stream):
    '''Return the given activity stream as a snippet of HTML.'''

    activity_list = [] # These are the activity stream messages.
    for activity in activity_stream:
        detail = None
        activity_type = activity['activity_type']
        # Some activity types may have details.
        if activity_type in activity_stream_actions_with_detail:
            details = logic.get_action('activity_detail_list')(context=context,
                data_dict={'id': activity['id']})
            # If an activity has just one activity detail then render the
            # detail instead of the activity.
            if len(details) == 1:
                detail = details[0]
                object_type = detail['object_type']

                if object_type == 'PackageExtra':
                    object_type = 'package_extra'

                new_activity_type = '%s %s' % (detail['activity_type'],
                                            object_type.lower())
                if new_activity_type in activity_stream_string_functions:
                    activity_type = new_activity_type

        if not activity_type in activity_stream_string_functions:
            raise NotImplementedError("No activity renderer for activity "
                "type '%s'" % str(activity_type))

        if not activity_type in activity_stream_string_icons:
                  raise NotImplementedError("No activity icon for activity "
                      "type '%s'" % str(activity_type))

        activity_msg = activity_stream_string_functions[activity_type]()
        activity_icon = activity_stream_string_icons[activity_type]

        # Get the data needed to render the message.
        matches = re.findall('\{([^}]*)\}', activity_msg)
        data = {}
        for match in matches:
            snippet = activity_snippet_functions[match](activity, detail)
            data[str(match)] = snippet
        activity_list.append({'msg': activity_msg,
                              'type': activity_type.replace(' ', '-').lower(),
                              'icon': activity_icon,
                              'data': data,
                              'timestamp': activity['timestamp']})
    return literal(base.render('activity_streams/activity_stream_items.html',
        extra_vars={'activities': activity_list}))
