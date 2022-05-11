import pandas as pd
import numpy as np
import os
import argparse
import pickle
from feature_extraction import Contours
from glob import glob
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


from dotenv import load_dotenv
from boto3 import resource

load_dotenv()
hasura_key = os.environ.get("HASURA_KEY")
s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")

resource_s3 = resource( 's3', 
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

bucket = resource_s3.Bucket(bucket_name)


# python rfr.py --inference --regressor-path /workspace/grape_rfr/regressor_model.pkl --csv-path /workspace/grape_rfr/sample_result.csv --image-path /workspace/regression_data/images1 --mask-path /workspace/regression_data/masks

def inference(regressor_path, csv_path, dest_path, image_path, mask_path, quality_id):
    """
    model_path : str
        RFR model path
    csv_path : str
        feature csv를 저장할 경로 ex) '/workspace/features.csv'
    """
    with open(regressor_path,"rb") as f:
        regressor = pickle.load(f)

    if os.path.isdir(image_path):
        image_path = [os.path.join(image_path, fname) for fname in os.listdir(image_path)]
    elif len(image_path) == 1:
        image_path = glob(os.path.expanduser(image_path))
        assert args.input, "The input path(s) was not found"
    
    features = Contours("","",dest_path=dest_path)
    for i in image_path:
        mask_name = i.split('/')[-1]+'_masks.pkl'
        save_path = f"{mask_path}{mask_name}"
        bucket.download_file(f"mask/{quality_id}/{mask_name}", save_path)
        features = Contours(save_path, i, dest_path, csv_path)
        features.run()
        os.remove(save_path)
    
    df = pd.read_csv(dest_path)
    X = df.drop(["image"], axis=1).values
    pred = regressor.predict(X)
    pred = pred.astype(int)
    pred_df = pd.DataFrame(pred)
    n = len(df.columns)
    df.insert(n,'predict',pred_df)
    # 거봉이나 샤인머스캣처럼 알 크기가 큰 포도는 포도알 개수는 37~50개 정도
    # df = pd.DataFrame({'Image':df["image"].to_numpy().reshape(-1), 'Predicted Values':pred.reshape(-1)})
    
    conditionlist = [
        (df.predict < 51),
        (df.predict >= 51)
    ]
    choicelist = ["false", "true"]
    df['Thinning'] = np.select(conditionlist, choicelist, default='Not Specified')
    # 물리적 상처가 있거나 크기가 작은 알, 병해충 피해를 본 알, 안쪽과 위쪽에 자라는 알 위주로 솎아주면 된다.
    df.to_csv(csv_path,index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Select inference/save mode')
    parser.add_argument('--train', action='store_true', default=False,
                        help='an integer for the accumulator')
    parser.add_argument('--inference',action='store_true', default=False,
                        help='sum the integers (default: find the max)')
    parser.add_argument('--regressor-path', type=str, default='regressor_model.pkl',
                        help='Trained regressor model path')
    parser.add_argument('--csv-path', type=str, default='/workspace/hue_test.csv',
                        help='csv file path where you want to save results')
    parser.add_argument('--dest-path', type=str, default='/workspace/hue_test.csv',
                        help='csv file path where you want to save results')
    
    parser.add_argument('--image-path', type=str, default='/workspace/regression_data/images3',
                        help='inference할 cropped된 포도 이미지 folder')
    parser.add_argument('--mask-path', type=str, default='/workspace/regression_data/masks',
                        help='inference할 mask 파일 folder')
    parser.add_argument('--quality-id', type=str, default='/workspace/regression_data/masks',
                        help='quality_id')
    args = parser.parse_args()
    if args.inference:
        inference(regressor_path = args.regressor_path, 
            csv_path=args.csv_path, dest_path=args.dest_path,
            image_path= args.image_path, mask_path=args.mask_path,
            quality_id=args.quality_id)
    # if args.train:
    #     train()