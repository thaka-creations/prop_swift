from rest_framework.exceptions import ErrorDetail
from rest_framework.utils.serializer_helpers import ReturnDict
from copy import deepcopy


def format_error(errors):
    if type(errors) == str:
        return errors
    elif (type(errors) == ReturnDict) or (type(errors) == dict):
        return get_error_message_from_dict(dict(errors))
    return get_error_message_from_dict(errors)


def get_error_message_from_dict(error):
    # print("unprocessed error:-> ", error)
    if type(error) == str:
        return error
    finished_processed_errors = []
    list_of_string_objects = [error]
    count = 0
    processing = True
    while processing:
        # print('list_of_string_objects:-> ', list_of_string_objects)
        for index, i in enumerate(list_of_string_objects):
            if type(i) == str:
                finished_processed_errors.append(list_of_string_objects.pop(index))
                continue
            if type(i) == dict:
                # print("object being processed:->", i)
                list_of_string_objects.append(recursive_dict_error(i))
                list_of_string_objects.pop(index)
            elif type(i) == list:
                # print("list in get_error_message_from_dict: deal with it!!! :-> ", error)
                list_of_string_objects.append(recursive_list_error(i))
                list_of_string_objects.pop(index)
            else:
                list_of_string_objects.append(str(i))
                list_of_string_objects.pop(index)
            del i
        count += 1
        if count > 20:
            processing = False
    # print('finished_processed_errors:-> ', finished_processed_errors)
    # print('finished_processed_errors:-> ', finished_processed_errors)
    final_error = ''.join(finished_processed_errors)
    return final_error


def recursive_dict_error(error):
    copy_of_error = deepcopy(error)
    if isinstance(error, dict):
        stored_keys = tuple(copy_of_error.keys())
        string_list_objects = []
        value_ = None
        for i in stored_keys:
            # print('type:-> ', type(copy_of_error[i]))
            if type(copy_of_error[i]) == list:
                # print('type:-> ', tuple(copy_of_error[i]))
                copy_of_error[i] = list(filter(None, copy_of_error[i]))
                for indiv in copy_of_error[i]:
                    if type(indiv) == ErrorDetail:
                        if i == 'non_field_errors':
                            value_ = str(indiv)
                        else:
                            value_ = str(i) + " : " + str(indiv)
                    else:
                        if i == 'non_field_errors':
                            value_ = recursive_dict_error(indiv)
                        else:
                            value_ = {i: recursive_dict_error(indiv)}
            elif type(copy_of_error[i]) == dict:
                value_ = {i: recursive_dict_error(copy_of_error[i])}
            elif type(copy_of_error[i]) == str:
                value_ = str(i) + " : " + str(copy_of_error[i])
            elif copy_of_error[i] is None:
                pass
            else:
                raise Exception(type(copy_of_error[i]))
        string_list_objects.append(value_)
        return string_list_objects
    return error


def recursive_list_error(error):
    if type(error) == list:
        return error[0]
    return error
