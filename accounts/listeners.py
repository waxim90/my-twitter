# 已经包装到 utils/listeners 下面了
# def user_changed(sender, instance, **kwargs):
#     # import 写在函数里面避免循环依赖
#     from accounts.services import UserService
#     UserService.invalidate_user_cache(instance.id)


def profile_changed(sender, instance, **kwargs):
    # import 写在函数里面避免循环依赖
    from accounts.services import UserService
    UserService.invalidate_profile_cache(instance.user_id)