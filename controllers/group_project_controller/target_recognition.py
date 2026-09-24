import cv2 
from pathlib import Path
from collections import defaultdict
from project_utils import ROOT, CONFIG

TEXTURES_DIR = ROOT / "textures"
MIN_MATCHES = 8 # confidence threshold 

orb = cv2.ORB_create(nfeatures=500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def load_ref_images():
    """Load target and distractor images from textrues folder
    
    Returns: 
        targets: dict {label: [image in grayscale]}
        distractors: dict {label: [image in grayscale]}
    """

    targets = defaultdict(list) # create dict
    for label in CONFIG["target_labels"]:
        path = TEXTURES_DIR / f"target_{label}.png"
        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"WARNING: could not load {path}")
            continue
        targets[label].append(img)

    distractors = defaultdict(list)
    distractor_dir = TEXTURES_DIR / "distractors"
    for path in distractor_dir.glob("*.png"): #matches all imgs in distractor folder 
        label = path.stem.rsplit("_", 1)[0] #since distractor images have multiples e.g. banana_a and banana_b
        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"WARNING: could load {path}")
            continue
        distractors[label].append(img)

    return dict(targets), dict(distractors)


# Load once at import, and precompute descriptors once rather than at every call
_targets, _distractors = load_ref_images()
_all_refs = {**_targets, **_distractors}

deleteme = 0


_ref_descriptors = {}
for _label, _images in _all_refs.items():
    _descs = []
    for _img in _images:
        _img_eq = cv2.equalizeHist(_img)
        if deleteme == 0:
            cv2.imwrite("debug_after_equalize_ref_img.png", _img)
            deleteme += 1
        _kp, _des = orb.detectAndCompute(_img_eq, None)
        if _des is not None:
            _descs.append(_des)
        _ref_descriptors[_label] = _descs

def score_all_labels(scene_bgr):
    """
    Compare the robot's captured frame (BGR) to every known reference label.
    Returns: 
        dict {label: best_match_score}
    """

    # get the robots captured scene (des_scene)
    scene_gray = cv2.cvtColor(scene_bgr, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("debug_before_equalize.png", scene_gray)  #BEFORE
    scene_gray = cv2.equalizeHist(scene_gray)
    cv2.imwrite("debug_after_equalize.png", scene_gray)   #AAFTER

    kp_scene, des_scene = orb.detectAndCompute(scene_gray, None)

    if des_scene is None:
        return None

    scores = {}
    for label, ref_descs in _ref_descriptors.items():
        best_for_label = 0
        for des_ref in ref_descs:
            matches = bf.match(des_ref, des_scene)
            good = [m for m in matches if m.distance < 50]
            best_for_label = max(best_for_label, len(good)) # gives the highest object match 
        scores[label] = best_for_label
    return scores 

def identify_target(camera_image, mission_target):
    """
    Given a raw BGR camera frame and the missions required target label, determine what
    is visible and whether that matches the mission target
    
    Returns: 
        is_target: bool - True if the best_match is the mission target with enough confidence
        best_label: str or None - label with the highest score, or None if nothing matches with more
        than the given confidence threshold (MIN_MATCHES)
        best_score: int - that label's score 
        """

    scores = score_all_labels(camera_image)

    if not scores:
        return False, None, 0

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    if best_score < MIN_MATCHES:
        return False, None, best_score
    
    is_target = (best_label == mission_target) #returns bool

    return is_target, best_label, best_score



