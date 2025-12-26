# import os.path as osp
# from collections import Counter

# import cv2
# import numpy as np
# import paddlers as pdrs
# from paddlers.tasks.utils.visualize import get_color_map_list
# from skimage.io import imsave

# from applications.common.path_global import md5_name, generate_url


# def execute(model_path, data_path, out_dir, test_names):
#     image_list = [osp.join(data_path, name) for name in test_names]
#     predictor = pdrs.deploy.Predictor(model_path, use_gpu=True)
#     pred = predictor.predict(image_list)
#     ims = [i['label_map'] for i in pred]
#     temps = list()
#     lut = np.array(get_color_map_list(256))
#     for idx, im in zip(range(len(image_list)), ims):
#         im = lut[im]
#         new_name = md5_name(test_names[idx])
#         imsave(osp.join(out_dir, new_name), np.uint8(im))
#         temps.append(generate_url + new_name)
#     return temps




# import os.path as osp
# from collections import Counter

# import cv2
# import numpy as np
# import os
# import paddle
# import paddlers as pdrs
# from paddle.inference import Config, create_predictor
# from paddlers.tasks.utils.visualize import get_color_map_list
# from skimage.io import imsave

# from applications.common.path_global import md5_name, generate_url


# def execute(model_path, data_path, out_dir, test_names):
#     image_list = [osp.join(data_path, name) for name in test_names]
#     debug = os.environ.get("CUGRS_SEG_DEBUG", "").strip() in ("1", "true", "True", "YES", "yes")
#     compiled = False
#     gpu_count = 0
#     try:
#         compiled = paddle.device.is_compiled_with_cuda()
#         gpu_count = paddle.device.cuda.device_count() if compiled else 0
#     except Exception:
#         compiled = False
#         gpu_count = 0
#     cvd = os.environ.get("CUDA_VISIBLE_DEVICES")
#     env_use_gpu = os.environ.get("CUGRS_USE_GPU", "").strip()
#     allow_gpu = (env_use_gpu in ("1", "true", "True", "YES", "yes"))
#     use_gpu = bool(allow_gpu and compiled and gpu_count > 0 and (cvd is None or str(cvd).strip() not in ("", "-1")))
#     model = pdrs.tasks.load_model(model_path, with_net=False)
#     transforms = getattr(model, 'test_transforms', None)
#     if transforms is None:
#         raise ValueError("Transforms need to be defined, now is None.")

#     if debug:
#         try:
#             tinfo = []
#             for op in transforms.transforms:
#                 tinfo.append(getattr(op, "__class__", type(op)).__name__)
#             print("[SEG-DEBUG] model_path:", model_path, flush=True)
#             print("[SEG-DEBUG] use_gpu:", use_gpu, "compiled:", compiled, "gpu_count:", gpu_count, "CVD:", cvd, flush=True)
#             print("[SEG-DEBUG] transforms:", " -> ".join(tinfo), flush=True)
#             print("[SEG-DEBUG] model_num_classes:", getattr(model, "num_classes", None), flush=True)
#         except Exception as e:
#             print("[SEG-DEBUG] transforms_dump_failed:", repr(e), flush=True)

#     preprocessed_samples = model.preprocess(image_list, transforms, to_tensor=False)
#     inputs = preprocessed_samples[0]
#     ori_shape = preprocessed_samples[1]
#     if debug:
#         try:
#             print("[SEG-DEBUG] inputs_shape:", getattr(inputs, "shape", None), "dtype:", getattr(inputs, "dtype", None), flush=True)
#             print("[SEG-DEBUG] inputs_minmax:", float(np.min(inputs)), float(np.max(inputs)), "mean:", float(np.mean(inputs)), flush=True)
#             print("[SEG-DEBUG] ori_shape:", ori_shape, flush=True)
#         except Exception as e:
#             print("[SEG-DEBUG] inputs_stats_failed:", repr(e), flush=True)

#     config = Config(osp.join(model_path, 'model.pdmodel'),
#                     osp.join(model_path, 'model.pdiparams'))
#     if use_gpu:
#         config.enable_use_gpu(200, 0)
#         config.switch_ir_optim(True)
#     else:
#         config.disable_gpu()
#         config.set_cpu_math_library_num_threads(1)
#     config.disable_glog_info()
#     config.enable_memory_optim()
#     config.switch_use_feed_fetch_ops(False)
#     predictor = create_predictor(config)

#     input_name = predictor.get_input_names()[0]
#     input_tensor = predictor.get_input_handle(input_name)
#     input_tensor.copy_from_cpu(inputs)

#     predictor.run()

#     output_names = predictor.get_output_names()
#     net_outputs = []
#     for name in output_names:
#         output_tensor = predictor.get_output_handle(name)
#         net_outputs.append(output_tensor.copy_to_cpu())
#     if debug:
#         try:
#             print("[SEG-DEBUG] output_names:", output_names, flush=True)
#             for i, arr in enumerate(net_outputs):
#                 print("[SEG-DEBUG] out", i, "shape:", arr.shape, "dtype:", arr.dtype, "minmax:", float(np.min(arr)), float(np.max(arr)), flush=True)
#                 if np.issubdtype(arr.dtype, np.integer):
#                     u, c = np.unique(arr, return_counts=True)
#                     idx = np.argsort(-c)[:10]
#                     top = [(int(u[j]), int(c[j])) for j in idx]
#                     print("[SEG-DEBUG] out", i, "top_labels:", top, flush=True)
#         except Exception as e:
#             print("[SEG-DEBUG] outputs_stats_failed:", repr(e), flush=True)

#     if len(net_outputs) == 1:
#         out = net_outputs[0]
#         if np.issubdtype(out.dtype, np.integer):
#             label_map = out
#             if label_map.ndim == 4 and label_map.shape[1] == 1:
#                 label_map = np.squeeze(label_map, axis=1)
#             label_map = label_map.astype('int32')
#             n, h, w = label_map.shape
#             inferred_classes = int(label_map.max()) + 1 if label_map.size else 0
#             model_classes = getattr(model, "num_classes", None)
#             if isinstance(model_classes, int) and model_classes > 0:
#                 num_classes = model_classes
#             else:
#                 num_classes = max(inferred_classes, 2)
#             score_map = np.zeros((n, h, w, num_classes), dtype='float32')
#             net_outputs = (label_map, score_map)
#         else:
#             logit = out
#             if logit.ndim == 4 and logit.shape[1] == 1:
#                 prob_pos = 1.0 / (1.0 + np.exp(-logit))
#                 label_map = (prob_pos > 0.5).astype('int32')
#                 label_map = np.squeeze(label_map, axis=1)
#                 prob = np.concatenate([1.0 - prob_pos, prob_pos], axis=1)
#                 score_map = np.transpose(prob, (0, 2, 3, 1))
#                 net_outputs = (label_map, score_map)
#             else:
#                 label_map = np.argmax(logit, axis=1).astype('int32')
#                 logit_max = np.max(logit, axis=1, keepdims=True)
#                 exp = np.exp(logit - logit_max)
#                 prob = exp / np.sum(exp, axis=1, keepdims=True)
#                 score_map = np.transpose(prob, (0, 2, 3, 1))
#                 net_outputs = (label_map, score_map)

#     label_maps, _ = model.postprocess(
#         net_outputs, batch_origin_shape=ori_shape, transforms=transforms.transforms)
#     ims = label_maps
#     if debug:
#         try:
#             for i, im in enumerate(ims[:3]):
#                 u, c = np.unique(im, return_counts=True)
#                 idx = np.argsort(-c)[:10]
#                 top = [(int(u[j]), int(c[j])) for j in idx]
#                 print("[SEG-DEBUG] post_label", i, "shape:", im.shape, "top_labels:", top, flush=True)
#         except Exception as e:
#             print("[SEG-DEBUG] post_stats_failed:", repr(e), flush=True)
#     temps = list()
#     lut = np.array(get_color_map_list(256))
#     for idx, im in zip(range(len(image_list)), ims):
#         im = lut[im]
#         new_name = md5_name(test_names[idx])
#         imsave(osp.join(out_dir, new_name), np.uint8(im))
#         temps.append(generate_url + new_name)
#     return temps


import os
import os.path as osp
import cv2
import json
import numpy as np
from skimage.io import imsave
from applications.common.path_global import md5_name, generate_url
import traceback

# Try importing ONNXRuntime
try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False

# Try importing Paddle
try:
    import paddlers
    from paddlers.tasks.segmenter import Segmenter
    HAS_PADDLE = True
except ImportError:
    HAS_PADDLE = False

def get_color_map_list(num_classes):
    """
    Returns the color map for visualizing the segmentation mask.
    """
    color_map = num_classes * [0, 0, 0]
    for i in range(0, num_classes):
        j = 0
        lab = i
        while lab:
            color_map[i * 3] |= (((lab >> 0) & 1) << (7 - j))
            color_map[i * 3 + 1] |= (((lab >> 1) & 1) << (7 - j))
            color_map[i * 3 + 2] |= (((lab >> 2) & 1) << (7 - j))
            j += 1
            lab >>= 3
    color_map = [color_map[i:i + 3] for i in range(0, len(color_map), 3)]
    return color_map

def get_preprocess_config(model_path):
    """
    Parse pipeline.json to get input size and normalization parameters.
    """
    pipeline_path = osp.join(model_path, 'pipeline.json')
    
    target_size = (1024, 1024) 
    mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
    std = np.array([58.395, 57.12, 57.375], dtype=np.float32)
    
    if osp.exists(pipeline_path):
        try:
            with open(pipeline_path, 'r') as f:
                pipeline = json.load(f)
                
            transforms = pipeline.get('pipeline', {}).get('transforms', [])
            if not transforms and 'transforms' in pipeline:
                 transforms = pipeline['transforms']

            for t in transforms:
                if t['type'] == 'Resize':
                    if 'size' in t:
                        size = t['size']
                        if isinstance(size, int):
                            target_size = (size, size)
                        elif isinstance(size, (list, tuple)):
                            if len(size) == 2:
                                target_size = (size[0], size[1])
                    if 'scale' in t:
                        scale = t['scale']
                        if isinstance(scale, (list, tuple)) and len(scale) == 2:
                            target_size = (scale[0], scale[1])

                if t['type'] == 'Normalize':
                    if 'mean' in t:
                        mean = np.array(t['mean'], dtype=np.float32)
                    if 'std' in t:
                        std = np.array(t['std'], dtype=np.float32)
                        
            print(f"Loaded config from {pipeline_path}: Size={target_size}, Mean={mean}, Std={std}")
        except Exception as e:
            print(f"Error parsing pipeline.json: {e}. Using defaults.")
    else:
        print(f"pipeline.json not found at {pipeline_path}. Using defaults: Size={target_size}")
        
    return target_size, mean, std

def preprocess_onnx(img_path, target_size, mean, std):
    """
    Preprocess for ONNX model with dynamic config, supporting TIF
    """
    # Use cv2.IMREAD_UNCHANGED to read TIF properly if it has >3 channels or 16-bit
    # However, for standard segmentation models trained on RGB, we usually want RGB.
    # So we stick to cv2.imread but handle potential errors better.
    
    img = cv2.imread(img_path) # Default reads as BGR, ignores alpha
    
    if img is None:
        # Try reading with IMREAD_UNCHANGED in case of weird TIF formats
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        
    if img is None:
        raise ValueError(f"Failed to load image: {img_path}")
    
    # Handle non-3-channel images (e.g. grayscale or RGBA or >3 channels)
    if img.ndim == 2: # Grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4: # RGBA
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    elif img.shape[2] == 3: # BGR
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Note: If image has > 4 channels (multispectral), we simply take first 3 for now 
    # as most standard models expect 3 channels.
    elif img.shape[2] > 3:
        img = img[:, :, :3]
        # Assuming first 3 are RGB-like, but in OpenCV it might be BGR order if loaded that way.
        # If loaded with UNCHANGED, channel order depends on file. 
        # For safety, let's assume it's roughly RGB-compatible or user needs to fine-tune.
        # But for TIF, cv2.imread usually converts to BGR.
        pass

    # Resize
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Normalize
    img = img.astype(np.float32)
    img = (img - mean) / std
    
    # HWC -> CHW
    img = img.transpose((2, 0, 1))
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

def execute_onnx(model_path, data_path, out_dir, test_names):
    """
    Execution logic for ONNX models
    """
    if not HAS_ORT:
        raise ImportError("onnxruntime is not installed.")

    if osp.isdir(model_path):
        onnx_path = osp.join(model_path, 'end2end.onnx')
    else:
        onnx_path = model_path
        model_path = osp.dirname(model_path) 
    
    if not osp.exists(onnx_path):
        raise FileNotFoundError(f"ONNX model not found at {onnx_path}")

    target_size, mean, std = get_preprocess_config(model_path)

    use_gpu = False
    if 'CUDA_VISIBLE_DEVICES' in os.environ:
        cvd = os.environ['CUDA_VISIBLE_DEVICES']
        if cvd and cvd != '-1':
            use_gpu = True
            
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_gpu else ['CPUExecutionProvider']
    try:
        session = ort.InferenceSession(onnx_path, providers=providers)
    except Exception as e:
        print(f"Failed to create InferenceSession with providers {providers}, falling back to CPU. Error: {e}")
        session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    temps = []
    lut = np.array(get_color_map_list(256))

    for name in test_names:
        img_path = osp.join(data_path, name)
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
                
            label_map = label_map.astype(np.int32)
            label_map = np.clip(label_map, 0, 255)
            color_img = lut[label_map]
            
            new_name = md5_name(name)
            save_path = osp.join(out_dir, new_name)
            # Save as PNG regardless of input format for browser compatibility
            if new_name.lower().endswith('.tif') or new_name.lower().endswith('.tiff'):
                 new_name = os.path.splitext(new_name)[0] + '.png'
                 
            save_path = osp.join(out_dir, new_name)
            imsave(save_path, np.uint8(color_img))
            temps.append(generate_url + new_name)
        except Exception as e:
            print(f"Error processing {name} with ONNX: {e}")
            traceback.print_exc()
            continue
            
    return temps

def execute_paddle(model_path, data_path, out_dir, test_names):
    if not HAS_PADDLE:
        raise ImportError("PaddleRS/PaddlePaddle is not installed.")

    predictor = paddlers.deploy.Predictor(model_dir=model_path, use_gpu=True)
    temps = []
    lut = np.array(get_color_map_list(256))
    
    for name in test_names:
        try:
            img_path = osp.join(data_path, name)
            pred = predictor.predict(img_file=img_path)
            label_map = pred['label_map']
            label_map = label_map.astype(np.int32) 
            label_map = np.clip(label_map, 0, 255) 
            color_img = lut[label_map]
            
            new_name = md5_name(name)
            save_path = osp.join(out_dir, new_name)
            imsave(save_path, np.uint8(color_img))
            temps.append(generate_url + new_name)
        except Exception as e:
            print(f"Error processing {name} with Paddle: {e}")
            continue
            
    return temps

def execute(model_path, data_path, out_dir, test_names):
    is_onnx = False
    if osp.isdir(model_path):
        if osp.exists(osp.join(model_path, 'end2end.onnx')):
            is_onnx = True
    elif model_path.endswith('.onnx'):
        is_onnx = True
        
    print(f"Executing model at {model_path}. Detected as ONNX: {is_onnx}")

    if is_onnx:
        return execute_onnx(model_path, data_path, out_dir, test_names)
    else:
        return execute_paddle(model_path, data_path, out_dir, test_names)