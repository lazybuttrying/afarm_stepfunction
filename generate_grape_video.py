import os
import subprocess

folder = "./grapes/"

#idx = 0
# sort 시 숫자는 문자열로 고려되어 1,10,2,3 순서로 됨을 주의하자 (사진이 날아갈 수 있음)
#for f in sorted(os.listdir(folder)):
#    os.rename(folder+f, folder+'%d.jpeg'%idx)
#    idx+=1

fps = 1
# 모든 사진의 이름이 해당 규칙을 만족해야함 (* 안 먹힘)
src = folder+"%d.jpeg"
dest = "result.mp4"
#ffmpeg는 리눅스 용으로 이를 파이썬으로 실행시키는 구조
subprocess.run(["ffmpeg", "-f", "image2",
    "-r", str(fps),
    "-i", src,
    "-crf", "22", # 고화질로
    "-vcodec", "mpeg4", # mp4 
    "-y", dest])
