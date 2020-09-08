#   dataAugmentation.py
#
#   Created on: September 2, 2020
#   Authors:   An Qu and Xenios Papademetris
#             {anq} <at> kth.se
#

import os
import sys
import csv
import numpy as np
import random as rd

# write your input files/parameters here-----------------------------------------------------------------------
# REQUIRED: enter the absolute path of the bisweb
# the ending folder should be bisweypython, e.g., /path/to/bisweb/biswebpython
bisweb_path = ''

# REQUIRED: enter the path of your input images and masks, ending with slash
mask_folder = ''
img_folder = ''

# REQUIRED: enter your output folder path, ending with slash
outputs_folder = ''

# OPTIONAL: enter the pair registration grid path, ending with slash
gridpath = ''

# REQUIRED: enter what kinds of augmentations you want to apply
# paddingf: if True then the code will pad images to pad_dim that should be specified below.
# crop: if True then the code will crop images to crp_dim that should be specified below.
# rotationNscalingf: if True then the code will randomly rotate and scale images.
# warpf: if True then the code will randowmly deform the images with guassian covariance cov that should be specified below.
#        You can specify the number of randomly deformed images per input image by N_rd below.
#        In order to avoid over augmented(distortion), please keep cov small(default=0.1)
# registerf: if True then the code will reslice the images with the grids in tha gridpath that should be specified above.
paddingf = True
cropf = True
rotationNscalingf = True
warpf = True
registerf = False

cov = 0.1
N_rd = 2
pad_dim = [88, 64, 78]
crp_dim = [64, 46, 78]
# write your input files/parameters here-----------------------------------------------------------------------


sys.path.append(os.path.abspath(bisweb_path+'/../build/native'));
sys.path.append(os.path.abspath(bisweb_path+'/../'));
import biswrapper as libbiswasm;
import biswebpython.core.bis_baseutils as bis_baseutils;
import biswebpython.core.bis_objects as bis;
libbis=bis_baseutils.getDynamicLibraryWrapper();





def padding(img, oup, tar_dim, inp_mask=None, oup_mask=None, inp_img2=None, oup_img2=None, pos=[0,0,0]):


    mri=bis.bisImage().load(img)
    dim=mri.dimensions

    new_dim=[]
    lpos=[]
    for i in range(3):
        if dim[i] < tar_dim[i]:
            new_dim.append(int(tar_dim[i]))
            lpos.append(int((tar_dim[i]-dim[i])/2))
        else:
            new_dim.append(int(dim[i]))
            lpos.append(0)

    new_arr=np.zeros(new_dim)



    if pos == None:
        new_arr[lpos[0]:lpos[0]+dim[0], \
                lpos[1]:lpos[1]+dim[1], \
                lpos[2]:lpos[2]+dim[2]] = mri.data_array

        new_img=mri.create(new_arr, mri.spacing, mri.affine)
        new_img.save(oup)

    else:
        new_arr[pos[0]:pos[0]+dim[0], \
                pos[1]:pos[1]+dim[1], \
                pos[2]:pos[2]+dim[2]] = mri.data_array

        new_img=mri.create(new_arr, mri.spacing, mri.affine)
        new_img.save(oup)

    if inp_mask:
        mask=bis.bisImage().load(inp_mask)
        dim_m=mask.dimensions
        new_arr_mask=np.zeros(new_dim)
        if pos == None:
            new_arr_mask[lpos[0]:lpos[0]+dim_m[0], \
                    lpos[1]:lpos[1]+dim_m[1], \
                    lpos[2]:lpos[2]+dim_m[2]] = mask.data_array
        else:
            new_arr_mask[pos[0]:pos[0]+dim_m[0], \
                    pos[1]:pos[1]+dim_m[1], \
                    pos[2]:pos[2]+dim_m[2]] = mask.data_array

        new_mask=mask.create(new_arr_mask, mask.spacing, mask.affine)
        new_mask.save(oup_mask)


    if inp_img2:
        img2=bis.bisImage().load(inp_img2)
        dim=img2.dimensions
        new_arr_img2=np.zeros(new_dim)
        new_arr_img2[lpos[0]:lpos[0]+dim[0], \
                lpos[1]:lpos[1]+dim[1], \
                lpos[2]:lpos[2]+dim[2]] = img2.data_array

        new_img2=img2.create(new_arr_img2, img2.spacing, img2.affine)
        new_img2.save(oup_img2)






def crop(img, oup, tar_dim, inp_mask=None, oup_mask=None, inp_img2=None, oup_img2=None, pos=[0,0,0]):
    mri=bis.bisImage().load(img)

    new_arr=mri.data_array[pos[0]:pos[0]+tar_dim[0], pos[1]:pos[1]+tar_dim[1], pos[2]:pos[2]+tar_dim[2]]

    new_img=mri.create(new_arr, mri.spacing, mri.affine)
    new_img.save(oup)

    if inp_mask:
        mask=bis.bisImage().load(inp_mask)

        new_arr_mask=mask.data_array[pos[0]:pos[0]+tar_dim[0], pos[1]:pos[1]+tar_dim[1], pos[2]:pos[2]+tar_dim[2]]

        new_mask=mask.create(new_arr_mask, mask.spacing, mask.affine)
        new_mask.save(oup_mask)

    if inp_img2:
        img2=bis.bisImage().load(inp_img2)

        new_arr_img2=img2.data_array[pos[0]:pos[0]+tar_dim[0], pos[1]:pos[1]+tar_dim[1], pos[2]:pos[2]+tar_dim[2]]

        new_img2=img2.create(new_arr_img2, img2.spacing, img2.affine)
        new_img2.save(oup_img2)






def rotNsc(inp_img, inp_mask, out_img, out_mask, inp_img2=False, out_img2=False):
    mri=bis.bisImage().load(inp_img);
    mask=bis.bisImage().load(inp_mask);

    if bool(inp_img2):
        mri2=bis.bisImage().load(inp_img2);

    dim=mri.dimensions;
    spa=mri.spacing;

    mask.data_array = mask.data_array * 10

    for n in range(2):
        if n==0:
            sign = -1
        else:
            sign = 1

        for idx in range(3):
            r=sign*rd.randrange(8, 15)

            rot=[0,0,0]
            rot[idx]=r

            for sc in range(4):
                scale=[1, 1, 1]
                if sc == 3:
                    scale=np.dot(scale, 1.08)
                else:
                    scale[sc]=1.2

                pvector=np.array([0,0,0,
                                  rot[0],rot[1],rot[2],
                                  scale[0],scale[1],scale[2],
                                  0,0,0],
                                  dtype=np.float32);

                tr_wasm=libbis.test_create_4x4matrix(mri,mri,pvector, { 'mode': 3},1);

                output_mri = libbis.resliceImageWASM(mri, tr_wasm, {
                "spacing" : [ spa[0],spa[1],spa[2] ],
                "dimensions" : [ dim[0],dim[1],dim[2] ],
                "interpolation" : 1 ,
                },True);

                output_mask = libbis.resliceImageWASM(mask, tr_wasm, {
                "spacing" : [ spa[0],spa[1],spa[2] ],
                "dimensions" : [ dim[0],dim[1],dim[2] ],
                "interpolation" : 1 ,
                },True);

                new_mask = bis.bisImage().create(output_mask.data_array.copy(), output_mask.spacing, output_mask.affine)
                for i in range(new_mask.dimensions[0]):
                    for j in range(new_mask.dimensions[1]):
                        for k in range(new_mask.dimensions[2]):
                            if new_mask.data_array[i][j][k] < 5:
                                new_mask.data_array[i][j][k] = 0
                            else:
                                new_mask.data_array[i][j][k] = 1

                suffix = "_x"+str(rot[0])+"_y"+str(rot[1])+"_z"+str(rot[2])+"_s"+str(sc)
                img_idx=out_img.index(".nii.gz")
                mask_idx=out_mask.index("_mask.nii.gz")
                out_img_name=out_img[:img_idx]+suffix+out_img[img_idx:]
                out_mask_name=out_mask[:mask_idx]+suffix+out_mask[mask_idx:]

                output_mri.save(out_img_name);
                new_mask.save(out_mask_name);

                if bool(inp_img2):
                    output_mri2 = libbis.resliceImageWASM(mri2, tr_wasm, {
                    "spacing" : [ spa[0],spa[1],spa[2] ],
                    "dimensions" : [ dim[0],dim[1],dim[2] ],
                    "interpolation" : 1 ,
                    },True);

                    img_idx2=out_img2.index(".nii.gz")
                    out_img_name2=out_img2[:img_idx2]+suffix+out_img2[img_idx2:]
                    output_mri2.save(out_img_name2);




def warp_img(inp_img, inp_mask, out_img, out_mask, inp_grid=False, cov=0.1, inp_img2=False, out_img2=False):

    mri=bis.bisImage().load(inp_img);
    mask=bis.bisImage().load(inp_mask);

    print('++++ \t input loaded from some.nii.gz, dims=',mri.dimensions);

    dim=mri.dimensions;
    spa=mri.spacing;

    mask.data_array = mask.data_array * 10

    # Create transformation
    nGrid=13
    spcGrid=1.2
    volsize=0.2

    if bool(inp_grid):

        gridfile=bis.bisComboTransformation()
        gridfile.load(inp_grid)
        grid=gridfile.grids

        # Reslicing --------------------------------------------------
        # 0=no interpolation (masks), 1=interpolation (for images)
        # Repeat for both MRI and mask
        temp_mri=mri
        temp_mask=mask
        for i in range(len(grid)):
            temp_mri = libbis.resliceImageWASM(temp_mri, grid[i], {
            "spacing" : [ spa[0],spa[1],spa[2] ],
            "dimensions" : [ dim[0],dim[1],dim[2] ],
            "interpolation" : 1 ,
            },True);

            temp_mask = libbis.resliceImageWASM(temp_mask, grid[i], {
            "spacing" : [ spa[0],spa[1],spa[2] ],
            "dimensions" : [ dim[0],dim[1],dim[2] ],
            "interpolation" : 1,
            },True);
        output_mri=temp_mri
        output_mask=temp_mask



    else:
        grid=bis.bisGridTransformation();
        grid.create(dim=np.array([nGrid,nGrid,nGrid]),spa=np.array([spcGrid,spcGrid,spcGrid]),ori=np.array([0,0,0]), usebspline=True);

        # Changes values in the displacement field
        displacements=grid.data_array;  # dimensions 125*3


        mean=[0,0,0]
        covariance=[[cov, 0, 0], [0, cov, 0], [0, 0, cov]]
        for i in range(nGrid):
            for j in range(nGrid):
                for k in range(nGrid):


                    [displacements[(i+j*nGrid+k*nGrid*nGrid)*3], displacements[(i+j*nGrid+k*nGrid*nGrid)*3+1], displacements[(i+j*nGrid+k*nGrid*nGrid)*3+2]] = np.random.multivariate_normal(mean, covariance)

        output_mri = libbis.resliceImageWASM(mri, grid, {
        "spacing" : [ spa[0],spa[1],spa[2] ],
        "dimensions" : [ dim[0],dim[1],dim[2] ],
        "interpolation" : 1 ,
        },True);

        output_mask = libbis.resliceImageWASM(mask, grid, {
        "spacing" : [ spa[0],spa[1],spa[2] ],
        "dimensions" : [ dim[0],dim[1],dim[2] ],
        "interpolation" : 1,
        },True);


    new_mask = bis.bisImage().create(output_mask.data_array.copy(), output_mask.spacing, output_mask.affine)
    for i in range(new_mask.dimensions[0]):
        for j in range(new_mask.dimensions[1]):
            for k in range(new_mask.dimensions[2]):
                if new_mask.data_array[i][j][k] < 5:
                    new_mask.data_array[i][j][k] = 0
                else:
                    new_mask.data_array[i][j][k] = 1


    output_mri.save(out_img);
    new_mask.save(out_mask);

    if bool(inp_img2):

        mri2=bis.bisImage().load(inp_img2);

        if bool(inp_grid):
            temp_mri2=mri2
            for i in range(len(grid)):
                temp_mri2 = libbis.resliceImageWASM(temp_mri2, grid[i], {
                "spacing" : [ spa[0],spa[1],spa[2] ],
                "dimensions" : [ dim[0],dim[1],dim[2] ],
                "interpolation" : 1 ,
                },True);
            output_mri2=temp_mri2

        else:
            output_mri2 = libbis.resliceImageWASM(mri2, grid, {
            "spacing" : [ spa[0],spa[1],spa[2] ],
            "dimensions" : [ dim[0],dim[1],dim[2] ],
            "interpolation" : 1 ,
            },True);

        output_mri2.save(out_img2)









if __name__ == '__main__':

    oup_img = outputs_folder + 'aug_img'
    oup_mask = outputs_folder + 'aug_mask'
    oup_il = outputs_folder + 'imageList.txt'
    oup_ml = outputs_folder + 'maskList.txt'
    os.mkdir(oup_img)
    os.mkdir(oup_mask)

    ib = []
    mb = []
    il = []
    ml = []


    for root, dirs, files in os.walk(mask_folder):
        if root == mask_folder:
            masks = files

            for i in masks:
                mb.append([root+i])
                ml.append([root+i])
                j = i.replace('_mask.nii.gz', '.nii.gz')
                ib.append([img_folder+j])
                il.append([img_folder+j])

                if paddingf:
                    padding(img_folder+j, oup_img+'/'+j.replace('.nii.gz', '_pad.nii.gz'), pad_dim, inp_mask=root+i, oup_mask=oup_mask+'/'+i.replace('_mask.nii.gz', '_pad_mask.nii.gz'))
                    ib.append([oup_img+'/'+j.replace('.nii.gz', '_pad.nii.gz')])
                    mb.append([oup_mask+'/'+i.replace('_mask.nii.gz', '_pad_mask.nii.gz')])
                    il.append([oup_img+'/'+j.replace('.nii.gz', '_pad.nii.gz')])
                    ml.append([oup_mask+'/'+i.replace('_mask.nii.gz', '_pad_mask.nii.gz')])

                if cropf:
                    crop(img_folder+j, oup_img+'/'+j.replace('.nii.gz', '_crop.nii.gz'), crp_dim, inp_mask=root+i, oup_mask=oup_mask+'/'+i.replace('_mask.nii.gz', '_crop_mask.nii.gz'))
                    ib.append([oup_img+'/'+j.replace('.nii.gz', '_crop.nii.gz')])
                    mb.append([oup_mask+'/'+i.replace('_mask.nii.gz', '_crop_mask.nii.gz')])
                    il.append([oup_img+'/'+j.replace('.nii.gz', '_crop.nii.gz')])
                    ml.append([oup_mask+'/'+i.replace('_mask.nii.gz', '_crop_mask.nii.gz')])


    for ele in ib:
        img = ele[0]
        msk_t = img.replace('aug_img', 'aug_mask')
        msk_tt = msk_t.replace(img_folder, mask_folder)
        msk = msk_tt.replace('.nii.gz', '_mask.nii.gz')

        if rotationNscalingf:
            rotNsc(img, msk, img.replace(img_folder, oup_img+'/'), msk.replace(mask_folder, oup_mask+'/'))

        if warpf:
            for ii in range(N_rd):
                i = ii + 1
                sfx = '_rd'+ str(i)
                imgop = img.replace(img_folder, oup_img+'/')
                mskop = msk.replace(mask_folder, oup_mask+'/')
                warp_img(img, msk, imgop.replace('.nii.gz', sfx+'.nii.gz'), mskop.replace('_mask.nii.gz', sfx+'_mask.nii.gz'), cov=cov)

    if registerf:
        for root1, dirs1, files1 in os.walk(gridpath):
            if root1 == gridpath:
                for grid in files1:
                    if 'results.txt' not in grid:
                        movi = grid.split('__')[1].replace('_mapped.grd', '.nii.gz')
                        movm = grid.split('__')[1].replace('_mapped.grd', '_mask.nii.gz')
                        warp_img(img_folder+movi, mask_folder+movm, oup_img+'/'+grid.replace('_mapped.grd', '.nii.gz'), oup_mask+'/'+grid.replace('_mapped.grd', '_mask.nii.gz'), inp_grid=root1+grid)

    for root2, dirs2, files2 in os.walk(oup_mask):
        if root2 == oup_mask:
            for file in files2:
                ml.append([root2 + '/' + file])
                il.append([root2.replace('aug_mask', 'aug_img') + '/' + file.replace('_mask.nii.gz', '.nii.gz')])

    with open(oup_il, 'w') as fi:
        fWriter = csv.writer(fi, lineterminator="\n")
        fWriter.writerows(il)

    with open(oup_ml, 'w') as fm:
        fWriter1 = csv.writer(fm, lineterminator="\n")
        fWriter1.writerows(ml)
