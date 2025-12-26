# import os

# from flask import Blueprint

# from applications.common.utils.http import success_api, fail_api
# from applications.interface.utils import get_model_info

# model_api = Blueprint('model_api', __name__, url_prefix='/api/model')


# @model_api.get('/list/<string:model_type>')
# def get_model_list(model_type):
#     types_list = {
#         "change_detection": "change_detector",
#         "classification": "classifier",
#         "image_restoration": "restorer",
#         "object_detection": "detector",
#         "semantic_segmentation": "segmenter"
#     }
#     if model_type not in types_list:
#         return fail_api("模型类型不正确")
#     model_list = []
#     if os.path.exists("model/{}".format(model_type)):
#         for dirname in os.listdir("model/{}".format(model_type)):
#             if not os.path.isdir("model/{}/{}".format(model_type, dirname)):
#                 continue
#             try:
#                 model_info = get_model_info("model/{}/{}".format(model_type,
#                                                                  dirname))
#                 if model_info["_Attributes"]["model_type"] == types_list[
#                         model_type]:
#                     model_list.append({
#                         "model_path": "model/{}/{}".format(model_type, dirname),
#                         "model_type": model_info["_Attributes"]["model_type"],
#                         "model_name": model_info["Model"]
#                     })
#             except:
#                 return fail_api("model/{}/{}下存放的模型格式非法，请检查".format(model_type,
#                                                                    dirname))
#     return success_api(data=model_list)



import os

from flask import Blueprint

from applications.common.utils.http import success_api, fail_api
from applications.interface.utils import get_model_info

model_api = Blueprint('model_api', __name__, url_prefix='/api/model')


@model_api.get('/list/<string:model_type>')
def get_model_list(model_type):
    types_list = {
        "change_detection": "change_detector",
        "classification": "classifier",
        "image_restoration": "restorer",
        "object_detection": "detector",
        "semantic_segmentation": "segmenter"
    }
    if model_type not in types_list:
        return fail_api("模型类型不正确")
    
    model_list = []
    
    # Helper function to scan a directory and append matching models
    def scan_models(folder_name, expected_types):
        base_path = "model/{}".format(folder_name)
        if not os.path.exists(base_path):
            return
            
        for dirname in os.listdir(base_path):
            full_path = os.path.join(base_path, dirname)
            if not os.path.isdir(full_path):
                continue
            try:
                # Use forward slashes for compatibility
                path_str = "model/{}/{}".format(folder_name, dirname)
                model_info = get_model_info(path_str)
                current_type = model_info["_Attributes"]["model_type"]
                
                if current_type in expected_types:
                    model_list.append({
                        "model_path": path_str,
                        "model_type": current_type,
                        "model_name": model_info["Model"]
                    })
            except Exception as e:
                # Log error but don't fail the whole request
                print(f"Error loading model info for {dirname}: {e}")
                pass

    # 1. Scan for the requested type
    scan_models(model_type, [types_list[model_type]])
    
    # 2. Special case: If requesting change_detection, also include semantic_segmentation models
    if model_type == "change_detection":
        scan_models("semantic_segmentation", ["segmenter"])
        
    return success_api(data=model_list)
