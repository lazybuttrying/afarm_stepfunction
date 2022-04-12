# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# python demo/demo.py --input /workspace/PlantDoc-Object-Detection-Dataset/TEST/vaccinium-angustifolium-low-bush-blueberry_0830_124221.jpg --output viz --opts MODEL.WEIGHTS /workspace/AdelaiDet/training_dir/BoxInst_MS_R_50_1x_plant3/model_0004999.pth --output-csv-config /workspace/AdelaiDet/config_csv.yaml
# python demo/demo.py --input /workspace/grape_label/test/9.png /workspace/grape_label/test/10.png --output viz/grape_from_real --opts MODEL.WEIGHTS /workspace/AdelaiDet/training_dir/BoxInst_MS_R_50_1x/model_final.pth --output-csv-config /workspace/AdelaiDet/config_csv.yaml

import argparse
import glob
import multiprocessing as mp
import os
import time
import cv2
import tqdm
import csv
import configparser

from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger

from predictor import VisualizationDemo
from adet.config import get_cfg

# constants
WINDOW_NAME = "COCO detections"

import sys
sys.path.append("/var/task/box")

def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    #args.config_file = '/var/task/box/configs/BoxInst/MS_R_50_1x.yaml'
    args.config_file = '/var/task/box/training_dir/BoxInst_MS_R_50_1x_sick4/config.yaml'
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.FCOS.INFERENCE_TH_TEST = args.confidence_threshold
    cfg.MODEL.MEInst.INFERENCE_TH_TEST = args.confidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = args.confidence_threshold
    cfg.freeze()
    return cfg


def get_parser():
    parser = argparse.ArgumentParser(description="Detectron2 Demo")
    parser.add_argument(
        "--config-file",
        default="/var/tast/box/configs/quick_schedules/e2e_mask_rcnn_R_50_FPN_inference_acc_test.yaml",
        metavar="FILE",
        help="path to config file",
    )
    parser.add_argument("--webcam", action="store_true", help="Take inputs from webcam.")
    parser.add_argument("--video-input", help="Path to video file.")
    parser.add_argument("--input", nargs="+", help="A list of space separated input images")

    parser.add_argument(
        "--output",
        default='/tmp/viz/',
        help="A file or directory to save output visualizations. "
        "If not given, will show output in an OpenCV window.",
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.3,
        help="Minimum score for instance predictions to be shown",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=[],
        nargs=argparse.REMAINDER,
    )
    parser.add_argument(
        "--output-csv-config",
        help="output file path and number of instances as csv",
        default = './config_csv.yaml'
    )
    parser.add_argument(
        "--code",
        help="the name of the report",
        default='68'
    )

    parser.add_argument("--mask-path",help="root file to save mask results",
        default='/tmp/regression_data/masks')

    return parser


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    args = get_parser().parse_args()
    csv_cfg = configparser.ConfigParser()  ## 클래스 객체 생성
    csv_cfg.read(args.output_csv_config)
    # args.output = './viz/'
    print(os.listdir('./'))
    csv_output_folder = f'/tmp/viz/results/{args.code}.csv'
    #csv_output_folder = csv_cfg.get("DEFAULT","OUTPUT_FOLDER")
    logger = setup_logger()
    logger.info("Arguments: " + str(args))
    f = open(csv_output_folder,'w', newline='')
    wr = csv.writer(f)
    csv_true = True
    mask_true = True
    path_true = True
    cfg = setup_cfg(args)

    demo = VisualizationDemo(cfg)
    mask_path = args.mask_path
    os.makedirs(mask_path, exist_ok=True)
    print(args.input)

    if args.input:
        if os.path.isdir(args.input[0]):
            args.input = [os.path.join(args.input[0], fname) for fname in os.listdir(args.input[0])]
        elif len(args.input) == 1:
            args.input = glob.glob(os.path.expanduser(args.input[0]))
            assert args.input, "The input path(s) was not found"
            
        for path in tqdm.tqdm(args.input, disable=not args.output):
            # use PIL, to be consistent with evaluation
            img = read_image(path, format="BGR")
            start_time = time.time()
            predictions, visualized_output, mask, pred_classes = \
                    demo.run_on_image(img, path, mask_path)
            
            # mask -> unit8 binary mask for every instances. 
            # 만약 class가 여러개라면 pred_claass도 같이 받아야함. 1 인 부분이 class

            img_path = path
            instance_num = len(predictions["instances"])
            row = []
            if csv_true:
                row.append(path)
                row.append(instance_num)
            if mask_true:
                row.append(mask)
                row.append(pred_classes)

            logger.info(
                "{}: detected {} instances in {:.2f}s".format(
                    path, len(predictions["instances"]), time.time() - start_time
                )
            )

            if args.output:
                if os.path.isdir(args.output):
                    assert os.path.isdir(args.output), args.output
                    out_filename = os.path.join(args.output, os.path.basename(path))
                else:
                    assert len(args.input) == 1, "Please specify a directory with args.output"
                    out_filename = args.output
                visualized_output.save(out_filename)
                print(f"visualized output saved to {out_filename}")
                if path_true:
                    row.append(out_filename)
            else:
                cv2.imshow(WINDOW_NAME, visualized_output.get_image()[:, :, ::-1])
                if cv2.waitKey(0) == 27:
                    break  # esc to quit
            wr.writerow(row)
        f.close()
        logger.info(
                "report saved to {}".format(
                    csv_output_folder
                )
            )
            

