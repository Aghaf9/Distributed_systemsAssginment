import cv2
from target_recognition import identify_target
from project_utils import ROOT

image = cv2.imread(str(ROOT / "controllers" / "group_project_controller" / "S1_view.png"))

is_target, label, score = identify_target(image, "soda_can")

print("Is target: ", is_target)
print("Best label detected: ", label)
print("Score: ", score)