from apps.drug.models import UserWorkSpace


def jwt_response_payload_handler(token, user=None, request=None):
    user_work_space = UserWorkSpace.objects.get(user=user)
    return {
        'token': token,
        'work_space_id': user_work_space.work_space.id
    }
