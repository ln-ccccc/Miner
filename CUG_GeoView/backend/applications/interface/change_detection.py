# import os
# import os.path as osp

# import numpy as np
# from skimage.io import imsave

# import paddlers as pdrs
# from paddlers.transforms import decode_image

# from applications.common.path_global import generate_url


# def execute(model_path, data_path, out_dir, names, window_size=256, stride=128):
#     image_list = [(osp.join(data_path, name["first"]), osp.join(data_path,
#                                                                 name["second"]))
#                   for name in names]
#     temps = list()  # 存储查看链接
#     temps1 = list()  # 存储生成的图片名
#     predictor = pdrs.deploy.Predictor(model_path, use_gpu=True)
#     for image in image_list:
#         predictor.slider_predict(
#             image,
#             save_dir=out_dir,
#             transforms=None,
#             block_size=window_size,  #注意block_size的值不能等于overlap的值
#             overlap=window_size - stride,
#             merge_strategy='accum')
#     for name in names:
#         raw_name = os.path.splitext(name["first"])[0] + ".tif"
#         img = decode_image(osp.join(out_dir, raw_name))
#         save_img = np.where(img == 0, img, 255)
#         save_img = np.concatenate((save_img, save_img, save_img), axis=-1)
#         imsave(osp.join(out_dir, name["first"]), save_img)
#         temps.append(generate_url + name["first"])
#         temps1.append(name["first"])
#         os.remove(osp.join(out_dir, raw_name))
#     return temps, temps1



# import os
# import os.path as osp
import numpy as np
import cv2
import traceback
import pandas as pd
from skimage.io import imsave

from applications.common.path_global import md5_name, generate_url
from applications.interface.semantic_segmentation import (
    get_preprocess_config, preprocess_onnx, 
    HAS_ORT, HAS_PADDLE
)

if HAS_ORT:
    import onnxruntime as ort
if HAS_PADDLE:
    import paddlers as pdrs

def predict_mask_onnx(session, img_path, target_size, mean, std):
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    
    try:
        input_tensor = preprocess_onnx(img_path, target_size, mean, std)
        outputs = session.run([output_name], {input_name: input_tensor})
        result = outputs[0]
        
        if result.ndim == 4:
            if result.shape[1] > 1:
                label_map = np.argmax(result, axis=1)
            else:
                label_map = result
            label_map = np.squeeze(label_map)
        else:
            label_map = np.squeeze(result)
            
        return label_map.astype(np.int32)
    except Exception as e:
        print(f"ONNX Prediction error for {img_path}: {e}")
        raise e

def predict_mask_paddle(predictor, img_path):
    try:
        res = predictor.predict(img_file=img_path)
        label_map = res['label_map']
        return label_map.astype(np.int32)
    except Exception as e:
        print(f"Paddle Prediction error for {img_path}: {e}")
        raise e

def compute_transfer_matrix(mask1, mask2):
    # Determine number of classes
    num_classes = max(np.max(mask1), np.max(mask2)) + 1
    
    # Resize mask2 to match mask1 if needed
    if mask1.shape != mask2.shape:
        mask2 = cv2.resize(mask2.astype(np.uint8), (mask1.shape[1], mask1.shape[0]), interpolation=cv2.INTER_NEAREST)
        
    mask1 = mask1.astype(np.int64)
    mask2 = mask2.astype(np.int64)
    
    # matrix[i, j] means transition from class i to class j
    matrix = np.zeros((num_classes, num_classes), dtype=np.int64)
    
    # Flatten
    m1 = mask1.flatten()
    m2 = mask2.flatten()
    
    # Filter valid
    valid = (m1 >= 0) & (m2 >= 0)
    m1 = m1[valid]
    m2 = m2[valid]
    
    # Compute counts
    # Using bincount for speed: index = m1 * num_classes + m2
    flat_indices = m1 * num_classes + m2
    counts = np.bincount(flat_indices, minlength=num_classes*num_classes)
    matrix = counts.reshape(num_classes, num_classes)
    
    return matrix

def execute(model_path, data_path, out_dir, names, window_size=256, stride=128):
    # 1. Determine Model Type
    is_onnx = False
    if osp.isdir(model_path):
        if osp.exists(osp.join(model_path, 'end2end.onnx')):
            is_onnx = True
    elif model_path.endswith('.onnx'):
        is_onnx = True
        
    print(f"Change Detection (via Segmentation): Using model at {model_path}. ONNX: {is_onnx}")
    
    # 2. Initialize Model
    session = None
    predictor = None
    target_size = (1024, 1024)
    mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
    std = np.array([58.395, 57.12, 57.375], dtype=np.float32)
    
    if is_onnx:
        if not HAS_ORT:
             raise ImportError("ONNXRuntime not installed")
        
        if osp.isdir(model_path):
            onnx_path = osp.join(model_path, 'end2end.onnx')
        else:
            onnx_path = model_path
            # If plain onnx file, assume config is in same dir
            model_path = osp.dirname(model_path) 
            
        target_size, mean, std = get_preprocess_config(model_path)
        
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        try:
            session = ort.InferenceSession(onnx_path, providers=providers)
        except:
            session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    else:
        if not HAS_PADDLE:
            raise ImportError("PaddlePaddle not installed")
        predictor = pdrs.deploy.Predictor(model_dir=model_path, use_gpu=True)

    temps = []
    temps1 = []
    
    for name_item in names:
        try:
            name1 = name_item["first"]
            name2 = name_item["second"]
            path1 = osp.join(data_path, name1)
            path2 = osp.join(data_path, name2)
            
            print(f"Processing pair: {name1} vs {name2}")
            
            # Predict
            if is_onnx:
                mask1 = predict_mask_onnx(session, path1, target_size, mean, std)
                mask2 = predict_mask_onnx(session, path2, target_size, mean, std)
            else:
                mask1 = predict_mask_paddle(predictor, path1)
                mask2 = predict_mask_paddle(predictor, path2)
            
            # Resize mask2 to mask1 if different (robustness)
            if mask1.shape != mask2.shape:
                mask2 = cv2.resize(mask2.astype(np.uint8), (mask1.shape[1], mask1.shape[0]), interpolation=cv2.INTER_NEAREST)

            # Generate Change Map (Binary: 0=No Change, 255=Change)
            change_map = (mask1 != mask2).astype(np.uint8) * 255
            
            # Save Change Map
            out_name = md5_name(name1) # Use name1's hash as base
            if not out_name.endswith('.png'):
                out_name = os.path.splitext(out_name)[0] + '.png'
            
            save_path = osp.join(out_dir, out_name)
            imsave(save_path, change_map)
            
            temps.append(generate_url + out_name)
            # temps1.append(out_name)
            temps1.append(out_name)
            
            # Compute and Save Transfer Matrix
            try:
                matrix = compute_transfer_matrix(mask1, mask2)
                matrix_name = os.path.splitext(out_name)[0] + '_matrix.csv'
                matrix_path = osp.join(out_dir, matrix_name)
                df = pd.DataFrame(matrix)
                df.to_csv(matrix_path, header=False, index=False)
                print(f"Saved transfer matrix to {matrix_path}")
            except Exception as e:
                print(f"Error computing matrix: {e}")
                
        except Exception as e:
            print(f"Error processing change detection for {name_item}: {e}")
            traceback.print_exc()
            continue
            
    return temps, temps1
