import os
import shutil

src_file = r'D:\Working\WorkingProject\08zhejiang\03shaoxing\01zhujirenmin_new\background\target\bm-0.0.1-SNAPSHOT.jar'
dst_dir = r'D:\Working\WorkingProject\08zhejiang\03shaoxing\01zhujirenmin_new\background\target\dabao\jar'
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)
else:
    shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)
shutil.copy(src_file, os.path.join(dst_dir, 'spd3.jar'))

src_dir = r'D:\Working\WorkingProject\08zhejiang\03shaoxing\01zhujirenmin_new\foreground\dist'
dst_dir = r'D:\Working\WorkingProject\08zhejiang\03shaoxing\01zhujirenmin_new\background\target\dabao\pc'
