import cv2
from target_recognition import load_ref_images
from project_utils import ROOT

targets, distractors = load_ref_images()
all_refs = {**targets, **distractors}

orb = cv2.ORB_create(nfeatures=500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) # uses hamming distance 

def score_all_labels(scene_gray, all_refs):

    #get the keypoints from captured image from robot
    scene_gray = cv2.equalizeHist(scene_gray)
    kp_scene, des_scene = orb.detectAndCompute(scene_gray, None)
    if des_scene is None:
        print("No keypoints found in this scene")
        return {}

    scores = {}
    for label, images in all_refs.items():
        best_for_label = 0
        for ref_img in images:
            ref_img = cv2.equalizeHist(ref_img)
            # get the kypoints from the ref images 
            kp_ref, des_ref = orb.detectAndCompute(ref_img, None)
            if des_ref is None:
                continue

            # get the best matches between scene and ref images 
            matches = bf.match(des_ref, des_scene)
            good = [m for m in matches if m.distance < 50]
            best_for_label = max(best_for_label, len(good))
        scores[label] = best_for_label
    return scores

scene = cv2.imread(str(ROOT / "controllers" / "group_project_controller" / "debug_frame_mug.png"), cv2.IMREAD_GRAYSCALE)
print(scene)
# scene = cv2.equalizeHist(scene)
scores = score_all_labels(scene, all_refs)

for label, score in sorted(scores.items(), key=lambda x: -x[1]):
    print(f"{label}: {score}")
