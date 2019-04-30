
from fastai import *
from fastai.vision import *

from skimage.transform import resize
from skimage.filters import threshold_otsu
from skimage.color import rgb2gray
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.segmentation import clear_border
from skimage.color import label2rgb

def crop2well(img, width=1380, plot=False):
#     img = np.asarray(PIL.Image.open(fn))
    bw = rgb2gray(img)
    thresh = threshold_otsu(bw)
    bw = closing(bw > thresh/3, square(3))
    label_image = label(bw)
    image_label_overlay = label2rgb(label_image, image=img)

    for region in regionprops(label_image):
        if region.area >= 100000:
            region_center = region.centroid[1]
            
    img_width = img.shape[1]    
    wid = width//2
    region_center = int(min(region_center, img.shape[1]-wid))
    region_center = int(max(region_center, wid))   
    offset = region_center-wid
#     print(region_center-wid, region_center+wid, offset)   
    img = img[:, region_center-wid:region_center+wid, :]
    return offset, img

def quarterImage(img,size=[800,800]):
    rs = size[0]
    cs = size[1]
    re = img.shape[0]-rs-1
    ce = img.shape[1]-cs-1
    imglist = []
    imglist.append(img[:rs,:cs,:])
    imglist.append(img[:rs,ce:-1,:])
    imglist.append(img[re:-1,:cs,:])
    imglist.append(img[re:-1,ce:-1,:])
    return imglist    
  
def mergeQuarterImage(imglist,size=[1380,1380]):
    rs, cs = imglist[0].shape[0], imglist[0].shape[1]
    rd, cd, rd_2, cd_2 = size[0], size[1], size[0]//2, size[1]//2
    rs0, rs1, rs2, rs3  = 0, rs-rd_2, rd_2, rs
    cs0, cs1, cs2, cs3  = 0, cs-cd_2, cd_2, cs     
    rd0, rd1, rd2  = 0, rd_2, rd
    cd0, cd1, cd2  = 0, cd_2, cd  

    img = np.zeros((*size,3))
  
    img[rd0:rd1, cd0:cd1, :] = imglist[0][rs0:rs2, cs0:cs2, :]   
    img[rd0:rd1, cd1:cd2, :] = imglist[1][rs0:rs2, cs1:cs3, :]
    img[rd1:rd2, cd0:cd1, :] = imglist[2][rs1:rs3, cs0:cs2, :]
    img[rd1:rd2, cd1:cd2, :] = imglist[3][rs1:rs3, cs1:cs3, :]
    
    return img    
  
def unetCountEggs(learn, img):
    # img = np.asarray(PIL.Image.open(fn))
    img = resize(img, (1380, 1920))
    offset, img = crop2well(img, width=1380, plot=False) 

    imglist = quarterImage(img) 
    pred_list= []
    for n,img in enumerate(imglist):
        PIL.Image.fromarray((255*img).astype(np.uint8)).save(f'app/data/q{n}.jpg')
        img_t = open_image(f'app/data/q{n}.jpg')
        print(f'predict {n}')
        pred_class,pred_idx,outputs = learn.predict(img_t)
        pred_list.append(pred_class.data.squeeze().numpy())

    for n,pred in enumerate(pred_list): 
        print(f'mask {n}')
        pred_list[n] = imglist[n]
        pred_list[n][pred==1] = [1,0,0]
        pred_list[n][pred==2] = [0,1,0]

    p_img = mergeQuarterImage(pred_list)
    
    return p_img

  
# fn = 'data/FEC-data/Images-Raw-Large/143263 - 1.jpg'
# fn = 'data/FEC-data/Images-Raw-Large/126780 - 1.jpg'
# fn = 'data/FEC-data/Images-Raw-Large/stacked.jpg'
# p_img = unetCountEggs(fn)  
# show_img(p_img,figsize=(12, 12))
# PIL.Image.fromarray((255*p_img).astype(np.uint8)).save(f'app/data/p_img.jpg')

# app/data/test.png